"""
Requirements Engineer Agent for Claude Code Multi-Agent Framework
Transforms user needs into structured specifications with SMART criteria and traceability
"""

import re
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import spacy

# Download required NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')


@dataclass
class Requirement:
    """Structured requirement representation"""
    id: str
    title: str
    description: str
    priority: str  # critical, high, medium, low
    status: str   # pending, in_progress, done
    acceptance_criteria: List[str]
    dependencies: List[str]
    user_story: str
    business_value: str
    technical_notes: str
    traceability_matrix: Dict[str, List[str]]
    created_at: str
    updated_at: str
    tags: List[str]


@dataclass
class UserStory:
    """User story structure following the 'As a... I want... So that...' format"""
    persona: str
    goal: str
    benefit: str
    acceptance_criteria: List[str]
    priority: int  # 1-5 scale


class RequirementsEngineerAgent:
    """
    Specialized agent for requirements engineering tasks:
    - Parse natural language requirements
    - Generate SMART feature definitions
    - Create user stories and acceptance criteria
    - Maintain traceability matrices
    - Detect ambiguities and suggest clarifications
    - Analyze dependencies between requirements
    """

    def __init__(self, project_path: str, memory_service_client=None):
        self.project_path = Path(project_path)
        self.memory_client = memory_service_client

        # Initialize directories
        self.reqs_dir = self.project_path / "source/reqs"
        self.db_path = self.project_path / ".claude-project/metrics/requirements_engineer.db"
        self.output_dir = self.project_path / ".claude-project/context"

        # Create directories
        self.reqs_dir.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize NLP tools
        self._init_nlp()

        # Initialize database
        self._init_database()

        # Load requirement patterns and templates
        self._load_templates()

    def _init_nlp(self):
        """Initialize natural language processing tools"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spacy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None

        self.stop_words = set(stopwords.words('english'))

        # Keywords for different requirement types
        self.functional_keywords = {'shall', 'will', 'must', 'should', 'can', 'function', 'feature', 'capability'}
        self.non_functional_keywords = {'performance', 'security', 'scalability', 'usability', 'reliability', 'availability'}
        self.priority_keywords = {
            'critical': {'critical', 'essential', 'mandatory', 'required'},
            'high': {'important', 'high', 'priority', 'urgent'},
            'medium': {'normal', 'medium', 'standard', 'typical'},
            'low': {'nice-to-have', 'optional', 'future', 'enhancement', 'low'}
        }

    def _init_database(self):
        """Initialize SQLite database for requirements management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Requirements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                priority TEXT,
                status TEXT,
                acceptance_criteria TEXT,
                dependencies TEXT,
                user_story TEXT,
                business_value TEXT,
                technical_notes TEXT,
                traceability_matrix TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                tags TEXT
            )
        """)

        # User stories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id TEXT,
                persona TEXT,
                goal TEXT,
                benefit TEXT,
                acceptance_criteria TEXT,
                priority INTEGER,
                created_at TIMESTAMP,
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            )
        """)

        # Dependencies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requirement_dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_req_id TEXT,
                target_req_id TEXT,
                dependency_type TEXT,  -- depends_on, blocks, relates_to
                description TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (source_req_id) REFERENCES requirements(id),
                FOREIGN KEY (target_req_id) REFERENCES requirements(id)
            )
        """)

        # Traceability table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traceability (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id TEXT,
                artifact_type TEXT,  -- feature, component, test, doc
                artifact_path TEXT,
                relationship TEXT,   -- implements, tests, documents
                created_at TIMESTAMP,
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            )
        """)

        conn.commit()
        conn.close()

    def _load_templates(self):
        """Load requirement templates and patterns"""
        self.requirement_templates = {
            'functional': {
                'pattern': "The system SHALL {action} {object} {condition}",
                'example': "The system SHALL authenticate users when they provide valid credentials"
            },
            'non_functional': {
                'pattern': "The system SHALL {metric} {threshold} {measurement}",
                'example': "The system SHALL respond within 2 seconds under normal load"
            },
            'user_story': {
                'pattern': "As a {persona}, I want {goal} so that {benefit}",
                'example': "As a user, I want to log in securely so that I can access my personal data"
            }
        }

    def parse_natural_language_requirements(self, text: str) -> List[Dict]:
        """
        Parse natural language text into structured requirements

        Args:
            text: Raw requirement text from user

        Returns:
            List of parsed requirements with structure and metadata
        """
        requirements = []

        # Split text into sentences
        sentences = sent_tokenize(text)

        for i, sentence in enumerate(sentences):
            # Skip very short sentences
            if len(sentence.split()) < 5:
                continue

            # Extract requirement information
            req_info = self._extract_requirement_info(sentence)

            if req_info['is_requirement']:
                requirement = {
                    'id': f"REQ-{str(i+1).zfill(3)}",
                    'raw_text': sentence,
                    'title': req_info['title'],
                    'description': req_info['description'],
                    'priority': req_info['priority'],
                    'type': req_info['type'],
                    'ambiguities': req_info['ambiguities'],
                    'suggested_improvements': req_info['suggestions']
                }
                requirements.append(requirement)

        return requirements

    def _extract_requirement_info(self, sentence: str) -> Dict:
        """Extract structured information from a requirement sentence"""
        info = {
            'is_requirement': False,
            'title': '',
            'description': sentence,
            'priority': 'medium',
            'type': 'functional',
            'ambiguities': [],
            'suggestions': []
        }

        # Check if sentence contains requirement indicators
        req_indicators = {'shall', 'will', 'must', 'should', 'can', 'need', 'require', 'enable', 'allow'}
        words = word_tokenize(sentence.lower())

        if any(indicator in words for indicator in req_indicators):
            info['is_requirement'] = True

            # Extract title (first 50 characters)
            info['title'] = sentence[:50] + "..." if len(sentence) > 50 else sentence

            # Detect priority
            info['priority'] = self._detect_priority(sentence)

            # Detect type (functional vs non-functional)
            info['type'] = self._detect_requirement_type(sentence)

            # Detect ambiguities
            info['ambiguities'] = self._detect_ambiguities(sentence)

            # Generate suggestions
            info['suggestions'] = self._generate_suggestions(sentence, info['ambiguities'])

        return info

    def _detect_priority(self, text: str) -> str:
        """Detect priority from requirement text"""
        text_lower = text.lower()

        for priority, keywords in self.priority_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return priority

        # Default priority based on modal verbs
        if any(word in text_lower for word in ['must', 'shall', 'critical', 'essential']):
            return 'critical'
        elif any(word in text_lower for word in ['should', 'important']):
            return 'high'
        else:
            return 'medium'

    def _detect_requirement_type(self, text: str) -> str:
        """Detect if requirement is functional or non-functional"""
        text_lower = text.lower()

        if any(keyword in text_lower for keyword in self.non_functional_keywords):
            return 'non_functional'
        else:
            return 'functional'

    def _detect_ambiguities(self, text: str) -> List[str]:
        """Detect potential ambiguities in requirement text"""
        ambiguities = []
        text_lower = text.lower()

        # Vague quantifiers
        vague_words = ['some', 'many', 'few', 'several', 'most', 'often', 'usually', 'normally', 'fast', 'slow', 'good', 'bad']
        for word in vague_words:
            if word in text_lower:
                ambiguities.append(f"Vague quantifier: '{word}' - consider specific measurements")

        # Missing actors
        if not any(actor in text_lower for actor in ['user', 'system', 'admin', 'operator', 'customer']):
            ambiguities.append("Missing actor - who performs this action?")

        # Passive voice detection (simplified)
        if ' be ' in text_lower or ' been ' in text_lower:
            ambiguities.append("Passive voice detected - consider active voice for clarity")

        # Missing conditions
        if 'when' not in text_lower and 'if' not in text_lower and 'after' not in text_lower:
            ambiguities.append("Missing conditions - when does this requirement apply?")

        return ambiguities

    def _generate_suggestions(self, text: str, ambiguities: List[str]) -> List[str]:
        """Generate suggestions for improving requirements"""
        suggestions = []

        # Suggest SMART criteria improvements
        if ambiguities:
            suggestions.append("Make requirement SMART: Specific, Measurable, Achievable, Relevant, Time-bound")

        # Suggest acceptance criteria
        if 'shall' in text.lower():
            suggestions.append("Add acceptance criteria to define 'done'")

        # Suggest user story format
        if not text.startswith('As a'):
            suggestions.append("Consider user story format: 'As a [persona], I want [goal] so that [benefit]'")

        return suggestions

    def create_user_stories(self, requirements: List[Dict]) -> List[UserStory]:
        """Convert requirements into user stories"""
        user_stories = []

        for req in requirements:
            # Extract personas from requirement text
            personas = self._extract_personas(req['description'])

            if not personas:
                personas = ['user']  # Default persona

            for persona in personas:
                user_story = self._generate_user_story(req, persona)
                user_stories.append(user_story)

        return user_stories

    def _extract_personas(self, text: str) -> List[str]:
        """Extract user personas from requirement text"""
        personas = []

        # Common persona patterns
        persona_patterns = [
            r'(?:as an?|for the)\s+(\w+(?:\s+\w+)*?)(?:\s+user|\s+role|\s*,)',
            r'(\w+(?:\s+\w+)*?)\s+(?:can|will|shall|should|must)',
            r'(?:user|customer|admin|operator|manager|developer)s?'
        ]

        text_lower = text.lower()

        for pattern in persona_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            personas.extend(matches)

        # Clean and deduplicate
        personas = list(set([p.strip() for p in personas if p.strip()]))

        return personas[:3]  # Limit to 3 personas per requirement

    def _generate_user_story(self, requirement: Dict, persona: str) -> UserStory:
        """Generate a user story from a requirement"""
        # Extract goal from requirement
        goal = self._extract_goal(requirement['description'])

        # Extract or infer benefit
        benefit = self._extract_benefit(requirement['description'])

        # Generate acceptance criteria
        acceptance_criteria = self._generate_acceptance_criteria(requirement)

        return UserStory(
            persona=persona,
            goal=goal,
            benefit=benefit,
            acceptance_criteria=acceptance_criteria,
            priority=self._map_priority_to_number(requirement['priority'])
        )

    def _extract_goal(self, text: str) -> str:
        """Extract the main goal from requirement text"""
        # Look for action verbs and objectives
        doc = self.nlp(text) if self.nlp else None

        if doc:
            # Find main verb and object
            main_verb = None
            main_obj = None

            for token in doc:
                if token.pos_ == 'VERB' and not main_verb:
                    main_verb = token.lemma_
                elif token.dep_ in ['dobj', 'pobj'] and not main_obj:
                    main_obj = token.text

            if main_verb and main_obj:
                return f"{main_verb} {main_obj}"

        # Fallback: extract first action phrase
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in ['authenticate', 'login', 'access', 'view', 'create', 'update', 'delete', 'manage']:
                return ' '.join(words[i:i+3])

        return text[:50]  # Fallback to truncated text

    def _extract_benefit(self, text: str) -> str:
        """Extract or infer the business benefit"""
        # Look for 'so that', 'to enable', 'in order to' patterns
        benefit_patterns = [
            r'(?:so that|to enable|in order to|to allow|to provide)\s+(.+)',
            r'(?:benefit|value|advantage):\s*(.+)'
        ]

        for pattern in benefit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Default benefits based on requirement type
        if 'authentication' in text.lower():
            return "I can securely access the system"
        elif 'search' in text.lower():
            return "I can quickly find relevant information"
        elif 'data' in text.lower():
            return "I can manage my information effectively"

        return "I can accomplish my goals efficiently"

    def _generate_acceptance_criteria(self, requirement: Dict) -> List[str]:
        """Generate acceptance criteria for a requirement"""
        criteria = []

        # Base criteria from requirement description
        text = requirement['description']

        # Add specific criteria based on requirement type
        if requirement.get('type') == 'functional':
            if 'authentication' in text.lower():
                criteria.extend([
                    "Given valid credentials, user can log in successfully",
                    "Given invalid credentials, system shows error message",
                    "Given successful login, user is redirected to dashboard"
                ])
            elif 'search' in text.lower():
                criteria.extend([
                    "Given search query, system returns relevant results",
                    "Given no matches, system shows 'no results' message",
                    "Given search results, user can navigate to items"
                ])

        # Generic criteria if none specific
        if not criteria:
            criteria = [
                f"Given the preconditions are met, the system performs the required action",
                f"Given error conditions, the system handles them gracefully",
                f"Given successful completion, the system confirms the result"
            ]

        return criteria[:5]  # Limit to 5 criteria

    def _map_priority_to_number(self, priority: str) -> int:
        """Map priority text to number (1-5)"""
        mapping = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        return mapping.get(priority.lower(), 3)

    def analyze_dependencies(self, requirements: List[Dict]) -> Dict[str, List[str]]:
        """Analyze dependencies between requirements"""
        dependencies = {}

        for req in requirements:
            req_id = req['id']
            dependencies[req_id] = []

            # Look for explicit dependencies
            dep_patterns = [
                r'depends on\s+(REQ-\d+)',
                r'requires\s+(REQ-\d+)',
                r'after\s+(REQ-\d+)',
                r'following\s+(REQ-\d+)'
            ]

            text = req['description'].lower()

            for pattern in dep_patterns:
                matches = re.findall(pattern, text)
                dependencies[req_id].extend(matches)

            # Infer logical dependencies
            # Authentication usually comes before other features
            if 'login' in text or 'authentication' in text:
                # This is likely a foundational requirement
                continue
            elif any(keyword in text for keyword in ['user', 'access', 'manage']):
                # Look for authentication requirements
                auth_reqs = [r for r in requirements if 'auth' in r['description'].lower()]
                if auth_reqs:
                    dependencies[req_id].extend([r['id'] for r in auth_reqs])

        return dependencies

    def generate_traceability_matrix(self, requirements: List[Dict]) -> Dict[str, Dict]:
        """Generate traceability matrix linking requirements to artifacts"""
        matrix = {}

        for req in requirements:
            req_id = req['id']
            matrix[req_id] = {
                'features': [],
                'components': [],
                'tests': [],
                'documentation': []
            }

            # Scan project files for requirement references
            source_dir = self.project_path / "source"
            if source_dir.exists():
                for file_path in source_dir.rglob('*'):
                    if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.md']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()

                            # Look for requirement references
                            if req_id in content:
                                rel_path = str(file_path.relative_to(self.project_path))

                                if 'test' in rel_path.lower():
                                    matrix[req_id]['tests'].append(rel_path)
                                elif file_path.suffix == '.md':
                                    matrix[req_id]['documentation'].append(rel_path)
                                else:
                                    matrix[req_id]['features'].append(rel_path)
                        except Exception:
                            continue

        return matrix

    def save_requirements_to_database(self, requirements: List[Dict], user_stories: List[UserStory], dependencies: Dict, traceability: Dict):
        """Save all requirements data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clear existing data
        cursor.execute("DELETE FROM requirements")
        cursor.execute("DELETE FROM user_stories")
        cursor.execute("DELETE FROM requirement_dependencies")
        cursor.execute("DELETE FROM traceability")

        # Insert requirements
        for req in requirements:
            req_obj = Requirement(
                id=req['id'],
                title=req.get('title', ''),
                description=req['description'],
                priority=req['priority'],
                status='pending',
                acceptance_criteria=json.dumps([]),
                dependencies=json.dumps(dependencies.get(req['id'], [])),
                user_story='',
                business_value='',
                technical_notes='',
                traceability_matrix=json.dumps(traceability.get(req['id'], {})),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=json.dumps(req.get('tags', []))
            )

            cursor.execute("""
                INSERT INTO requirements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(asdict(req_obj).values()))

        # Insert user stories
        for story in user_stories:
            cursor.execute("""
                INSERT INTO user_stories (requirement_id, persona, goal, benefit, acceptance_criteria, priority, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                'REQ-001',  # Link to first requirement for now
                story.persona,
                story.goal,
                story.benefit,
                json.dumps(story.acceptance_criteria),
                story.priority,
                datetime.now().isoformat()
            ))

        conn.commit()
        conn.close()

    def generate_functional_requirements_document(self, requirements: List[Dict], user_stories: List[UserStory], dependencies: Dict) -> str:
        """Generate a comprehensive functional requirements document"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        project_name = self.project_path.name

        doc = f"""# Functional Requirements Specification

**Project**: {project_name}
**Version**: 1.0
**Date**: {timestamp}
**Status**: Draft
**Generated by**: Requirements Engineer Agent

## 1. Executive Summary

### 1.1 Purpose
This document defines the functional requirements for {project_name} as analyzed and structured by the Requirements Engineer Agent.

### 1.2 Scope
The system encompasses the following key areas:
"""

        # Add scope based on requirements
        areas = set()
        for req in requirements:
            if 'authentication' in req['description'].lower():
                areas.add('User Authentication and Authorization')
            if 'data' in req['description'].lower():
                areas.add('Data Management')
            if 'search' in req['description'].lower():
                areas.add('Search and Discovery')
            if 'api' in req['description'].lower():
                areas.add('API Services')

        for area in sorted(areas):
            doc += f"- **{area}**\n"

        doc += f"""

## 2. Requirements Overview

### 2.1 Summary Statistics
- **Total Requirements**: {len(requirements)}
- **Critical Priority**: {sum(1 for r in requirements if r['priority'] == 'critical')}
- **High Priority**: {sum(1 for r in requirements if r['priority'] == 'high')}
- **Medium Priority**: {sum(1 for r in requirements if r['priority'] == 'medium')}
- **Low Priority**: {sum(1 for r in requirements if r['priority'] == 'low')}

## 3. Functional Requirements

"""

        # Group requirements by priority
        grouped_reqs = {}
        for req in requirements:
            priority = req['priority']
            if priority not in grouped_reqs:
                grouped_reqs[priority] = []
            grouped_reqs[priority].append(req)

        # Add requirements by priority
        priority_order = ['critical', 'high', 'medium', 'low']
        for priority in priority_order:
            if priority in grouped_reqs:
                doc += f"### 3.{priority_order.index(priority)+1} {priority.title()} Priority Requirements\n\n"

                for req in grouped_reqs[priority]:
                    doc += f"#### {req['id']}: {req['title']}\n"
                    doc += f"**Priority**: {priority.title()}  \n"
                    doc += f"**Description**: {req['description']}\n\n"

                    if req.get('ambiguities'):
                        doc += "**Potential Ambiguities**:\n"
                        for amb in req['ambiguities']:
                            doc += f"- {amb}\n"
                        doc += "\n"

                    if req.get('suggested_improvements'):
                        doc += "**Suggested Improvements**:\n"
                        for sugg in req['suggested_improvements']:
                            doc += f"- {sugg}\n"
                        doc += "\n"

                    if dependencies.get(req['id']):
                        doc += f"**Dependencies**: {', '.join(dependencies[req['id']])}\n\n"

                    doc += "---\n\n"

        # Add user stories section
        doc += "## 4. User Stories\n\n"
        for i, story in enumerate(user_stories, 1):
            doc += f"### US-{i:03d}: {story.persona.title()} Story\n"
            doc += f"**As a** {story.persona}, **I want** {story.goal} **so that** {story.benefit}\n\n"
            doc += "**Acceptance Criteria**:\n"
            for criterion in story.acceptance_criteria:
                doc += f"- {criterion}\n"
            doc += f"\n**Priority**: {story.priority}/5\n\n"
            doc += "---\n\n"

        # Add dependencies section
        doc += "## 5. Requirement Dependencies\n\n"
        doc += "| Requirement | Dependencies |\n"
        doc += "|-------------|-------------|\n"
        for req_id, deps in dependencies.items():
            dep_str = ', '.join(deps) if deps else 'None'
            doc += f"| {req_id} | {dep_str} |\n"

        # Add next steps
        doc += """

## 6. Implementation Recommendations

### 6.1 Development Phases
1. **Phase 1**: Implement critical priority requirements
2. **Phase 2**: Add high priority features
3. **Phase 3**: Complete medium and low priority items

### 6.2 Quality Assurance
- Each requirement should have corresponding acceptance tests
- Traceability should be maintained throughout development
- Regular requirement reviews should be conducted

### 6.3 Risk Mitigation
- Address ambiguous requirements first
- Implement dependency requirements before dependent ones
- Regular stakeholder validation

## 7. Glossary

Terms and definitions will be maintained as requirements evolve.

---
*This document was generated by the Requirements Engineer Agent and should be reviewed by stakeholders.*
"""

        return doc

    def store_in_memory_service(self, requirements: List[Dict], user_stories: List[UserStory]):
        """Store requirements analysis in memory service for cross-session persistence"""
        if not self.memory_client:
            return

        # Store high-level analysis
        summary = {
            'total_requirements': len(requirements),
            'critical_count': sum(1 for r in requirements if r['priority'] == 'critical'),
            'user_stories_count': len(user_stories),
            'project': self.project_path.name,
            'analysis_date': datetime.now().isoformat()
        }

        self.memory_client.store_memory(
            content=f"Requirements analysis for {self.project_path.name}: {json.dumps(summary, indent=2)}",
            tags=[
                f"project:{self.project_path.name}",
                "type:requirements-analysis",
                "agent:requirements-engineer",
                "priority:high"
            ],
            importance=0.8
        )

        # Store individual critical requirements
        for req in requirements:
            if req['priority'] == 'critical':
                self.memory_client.store_memory(
                    content=f"Critical Requirement {req['id']}: {req['description']}",
                    tags=[
                        f"project:{self.project_path.name}",
                        f"requirement:{req['id']}",
                        "type:critical-requirement",
                        "agent:requirements-engineer"
                    ],
                    importance=0.9
                )

    def process_requirements(self, input_text: str) -> Dict[str, Any]:
        """
        Main processing pipeline for requirements engineering

        Args:
            input_text: Raw requirements input from user

        Returns:
            Complete analysis results
        """
        print("🔍 Parsing natural language requirements...")
        requirements = self.parse_natural_language_requirements(input_text)

        print("📖 Creating user stories...")
        user_stories = self.create_user_stories(requirements)

        print("🔗 Analyzing dependencies...")
        dependencies = self.analyze_dependencies(requirements)

        print("📊 Generating traceability matrix...")
        traceability = self.generate_traceability_matrix(requirements)

        print("💾 Saving to database...")
        self.save_requirements_to_database(requirements, user_stories, dependencies, traceability)

        print("📋 Generating documentation...")
        doc = self.generate_functional_requirements_document(requirements, user_stories, dependencies)

        # Save functional requirements document
        output_file = self.reqs_dir / "functional-requirements.md"
        with open(output_file, 'w') as f:
            f.write(doc)

        print("🧠 Storing in memory service...")
        self.store_in_memory_service(requirements, user_stories)

        return {
            'requirements': requirements,
            'user_stories': [asdict(story) for story in user_stories],
            'dependencies': dependencies,
            'traceability': traceability,
            'output_file': str(output_file),
            'total_requirements': len(requirements),
            'critical_requirements': sum(1 for r in requirements if r['priority'] == 'critical'),
            'ambiguities_found': sum(len(r.get('ambiguities', [])) for r in requirements),
            'suggestions_count': sum(len(r.get('suggested_improvements', [])) for r in requirements)
        }


def main():
    """CLI entry point for requirements engineer agent"""
    import sys
    if len(sys.argv) < 3:
        print("Usage: python requirements_engineer_agent.py <project_path> <requirements_text>")
        sys.exit(1)

    project_path = sys.argv[1]
    requirements_text = sys.argv[2]

    agent = RequirementsEngineerAgent(project_path)
    results = agent.process_requirements(requirements_text)

    print(f"\n✅ Requirements Analysis Complete!")
    print(f"📊 Total Requirements: {results['total_requirements']}")
    print(f"🚨 Critical Requirements: {results['critical_requirements']}")
    print(f"⚠️  Ambiguities Found: {results['ambiguities_found']}")
    print(f"💡 Suggestions Generated: {results['suggestions_count']}")
    print(f"📄 Output: {results['output_file']}")


if __name__ == "__main__":
    main()