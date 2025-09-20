/**
 * Context Formatting Utility
 * Formats memories for injection into Claude Code sessions
 */

/**
 * Detect if running in Claude Code CLI environment
 */
function isCLIEnvironment() {
    // Check for Claude Code specific environment indicators
    return process.env.CLAUDE_CODE_CLI === 'true' || 
           process.env.TERM_PROGRAM === 'claude-code' ||
           process.argv.some(arg => arg.includes('claude')) ||
           (process.stdout.isTTY === false); // Explicitly check for non-TTY contexts
}

/**
 * ANSI Color codes for CLI formatting
 */
const COLORS = {
    RESET: '\x1b[0m',
    BRIGHT: '\x1b[1m',
    DIM: '\x1b[2m',
    CYAN: '\x1b[36m',
    GREEN: '\x1b[32m',
    BLUE: '\x1b[34m',
    YELLOW: '\x1b[33m',
    MAGENTA: '\x1b[35m',
    GRAY: '\x1b[90m'
};

/**
 * Convert markdown formatting to ANSI color codes for terminal display
 * Provides clean, formatted output without raw markdown syntax
 */
function convertMarkdownToANSI(text, options = {}) {
    const {
        stripOnly = false,  // If true, only strip markdown without adding ANSI
        preserveStructure = true  // If true, maintain line breaks and spacing
    } = options;
    
    if (!text || typeof text !== 'string') {
        return text;
    }
    
    // Check if markdown conversion is disabled via environment
    if (process.env.CLAUDE_MARKDOWN_TO_ANSI === 'false') {
        return text;
    }
    
    let processed = text;
    
    // Process headers (must be done before other replacements)
    // H1: # Header -> Bold Cyan
    processed = processed.replace(/^#\s+(.+)$/gm, (match, content) => {
        return stripOnly ? content : `${COLORS.BRIGHT}${COLORS.CYAN}${content}${COLORS.RESET}`;
    });
    
    // H2: ## Header -> Bold Cyan (slightly different from H1 in real terminal apps)
    processed = processed.replace(/^##\s+(.+)$/gm, (match, content) => {
        return stripOnly ? content : `${COLORS.BRIGHT}${COLORS.CYAN}${content}${COLORS.RESET}`;
    });
    
    // H3: ### Header -> Bold
    processed = processed.replace(/^###\s+(.+)$/gm, (match, content) => {
        return stripOnly ? content : `${COLORS.BRIGHT}${content}${COLORS.RESET}`;
    });
    
    // H4-H6: #### Header -> Bold (but could be differentiated if needed)
    processed = processed.replace(/^#{4,6}\s+(.+)$/gm, (match, content) => {
        return stripOnly ? content : `${COLORS.BRIGHT}${content}${COLORS.RESET}`;
    });
    
    // Bold text: **text** or __text__
    processed = processed.replace(/\*\*([^*]+)\*\*/g, (match, content) => {
        return stripOnly ? content : `${COLORS.BRIGHT}${content}${COLORS.RESET}`;
    });
    processed = processed.replace(/__([^_]+)__/g, (match, content) => {
        return stripOnly ? content : `${COLORS.BRIGHT}${content}${COLORS.RESET}`;
    });
    
    // Code blocks MUST be processed before inline code to avoid conflicts
    // Code blocks: ```language\ncode\n```
    processed = processed.replace(/```(\w*)\n?([\s\S]*?)```/g, (match, lang, content) => {
        if (stripOnly) {
            return content.trim();
        }
        const lines = content.trim().split('\n').map(line => 
            `${COLORS.GRAY}${line}${COLORS.RESET}`
        );
        return lines.join('\n');
    });
    
    // Italic text: *text* or _text_ (avoiding URLs and bold syntax)
    // More conservative pattern to avoid matching within URLs
    processed = processed.replace(/(?<!\*)\*(?!\*)([^*\n]+)(?<!\*)\*(?!\*)/g, (match, content) => {
        return stripOnly ? content : `${COLORS.DIM}${content}${COLORS.RESET}`;
    });
    processed = processed.replace(/(?<!_)_(?!_)([^_\n]+)(?<!_)_(?!_)/g, (match, content) => {
        return stripOnly ? content : `${COLORS.DIM}${content}${COLORS.RESET}`;
    });
    
    // Inline code: `code` (after code blocks to avoid matching backticks in blocks)
    processed = processed.replace(/`([^`]+)`/g, (match, content) => {
        return stripOnly ? content : `${COLORS.GRAY}${content}${COLORS.RESET}`;
    });
    
    // Lists: Convert markdown bullets to better symbols
    // Unordered lists: - item or * item
    processed = processed.replace(/^[\s]*[-*]\s+(.+)$/gm, (match, content) => {
        return stripOnly ? content : `  ${COLORS.CYAN}•${COLORS.RESET} ${content}`;
    });
    
    // Ordered lists: 1. item
    processed = processed.replace(/^[\s]*\d+\.\s+(.+)$/gm, (match, content) => {
        return stripOnly ? content : `  ${COLORS.CYAN}›${COLORS.RESET} ${content}`;
    });
    
    // Links: [text](url) - process before blockquotes so links in quotes work
    processed = processed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, text, url) => {
        return stripOnly ? text : `${COLORS.CYAN}${text}${COLORS.RESET}`;
    });
    
    // Blockquotes: > quote
    processed = processed.replace(/^>\s+(.+)$/gm, (match, content) => {
        return stripOnly ? content : `${COLORS.DIM}│ ${content}${COLORS.RESET}`;
    });
    
    // Horizontal rules: --- or *** or ___
    processed = processed.replace(/^[-*_]{3,}$/gm, () => {
        return stripOnly ? '' : `${COLORS.DIM}${'─'.repeat(40)}${COLORS.RESET}`;
    });
    
    // Clean up any double resets or color artifacts
    processed = processed.replace(/(\x1b\[0m)+/g, COLORS.RESET);
    
    return processed;
}

/**
 * Format memories for CLI environment with enhanced visual formatting
 */
function formatMemoriesForCLI(memories, projectContext, options = {}) {
    const {
        includeProjectSummary = true,
        maxMemories = 8,
        includeTimestamp = true,
        maxContentLengthCLI = 400,
        maxContentLengthCategorized = 350,
        storageInfo = null
    } = options;

    if (!memories || memories.length === 0) {
        return `${COLORS.CYAN}┌─${COLORS.RESET} 🧠 Memory Context\n${COLORS.CYAN}└─${COLORS.RESET} No relevant memories found for this session.\n`;
    }

    // Filter out null/generic memories and limit number
    const validMemories = [];
    let memoryIndex = 0;
    
    for (const memory of memories) {
        if (validMemories.length >= maxMemories) break;
        
        const formatted = formatMemoryForCLI(memory, memoryIndex, {
            maxContentLength: maxContentLengthCLI,
            includeDate: includeTimestamp
        });
        
        if (formatted) {
            validMemories.push({ memory, formatted });
            memoryIndex++;
        }
    }

    let contextMessage = `${COLORS.CYAN}┌─${COLORS.RESET} 🧠 ${COLORS.BRIGHT}Memory Context${COLORS.RESET}`;
    
    // Add project summary in enhanced CLI format
    if (includeProjectSummary && projectContext) {
        const { name, frameworks, tools, branch, lastCommit } = projectContext;
        const projectInfo = [];
        if (name) projectInfo.push(name);
        if (frameworks?.length) projectInfo.push(frameworks.join(', '));
        if (tools?.length) projectInfo.push(tools.join(', '));
        
        contextMessage += ` ${COLORS.DIM}→${COLORS.RESET} ${COLORS.BLUE}${projectInfo.join(', ')}${COLORS.RESET}\n`;
        contextMessage += `${COLORS.CYAN}│${COLORS.RESET}\n`;
        
        if (branch || lastCommit) {
            const gitInfo = [];
            if (branch) gitInfo.push(`${COLORS.GREEN}${branch}${COLORS.RESET}`);
            if (lastCommit) gitInfo.push(`${COLORS.GRAY}${lastCommit.substring(0, 7)}${COLORS.RESET}`);
            contextMessage += `${COLORS.CYAN}├─${COLORS.RESET} 📂 ${gitInfo.join(' • ')}\n`;
        }
        
        // Add storage information if available
        if (storageInfo) {
            const locationText = storageInfo.location.length > 40 ? 
                storageInfo.location.substring(0, 37) + '...' : 
                storageInfo.location;
            
            // Show rich storage info if health data is available
            if (storageInfo.health && storageInfo.health.totalMemories > 0) {
                const memoryInfo = `${storageInfo.health.totalMemories} memories`;
                const sizeInfo = storageInfo.health.databaseSizeMB > 0 ? `, ${storageInfo.health.databaseSizeMB}MB` : '';
                contextMessage += `${COLORS.CYAN}├─${COLORS.RESET} ${storageInfo.icon} ${COLORS.BRIGHT}${storageInfo.description}${COLORS.RESET} ${COLORS.GRAY}(${memoryInfo}${sizeInfo})${COLORS.RESET}\n`;
                contextMessage += `${COLORS.CYAN}├─${COLORS.RESET} 📍 ${COLORS.GRAY}${locationText}${COLORS.RESET}\n`;
            } else {
                contextMessage += `${COLORS.CYAN}├─${COLORS.RESET} ${storageInfo.icon} ${COLORS.BRIGHT}${storageInfo.description}${COLORS.RESET} ${COLORS.GRAY}(${locationText})${COLORS.RESET}\n`;
            }
        }
    } else {
        contextMessage += '\n';
        contextMessage += `${COLORS.CYAN}│${COLORS.RESET}\n`;
    }
    
    contextMessage += `${COLORS.CYAN}├─${COLORS.RESET} 📚 ${COLORS.BRIGHT}${validMemories.length} memories loaded${COLORS.RESET}\n`;
    contextMessage += `${COLORS.CYAN}│${COLORS.RESET}\n`;
    
    if (validMemories.length > 3) {
        // Group by category with enhanced formatting
        const categories = groupMemoriesByCategory(validMemories.map(v => v.memory));
        
        const categoryInfo = {
            gitContext: { title: 'Current Development', icon: '⚡', color: COLORS.BRIGHT },
            recent: { title: 'Recent Work (Last 7 days)', icon: '🕒', color: COLORS.GREEN },
            decisions: { title: 'Architecture & Design', icon: '🏗️', color: COLORS.YELLOW },
            architecture: { title: 'Architecture & Design', icon: '🏗️', color: COLORS.YELLOW }, 
            insights: { title: 'Key Insights', icon: '💡', color: COLORS.MAGENTA },
            bugs: { title: 'Bug Fixes & Issues', icon: '🐛', color: COLORS.GREEN },
            features: { title: 'Features & Implementation', icon: '✨', color: COLORS.BLUE },
            other: { title: 'Additional Context', icon: '📝', color: COLORS.GRAY }
        };
        
        let hasContent = false;
        let categoryCount = 0;
        const totalCategories = Object.values(categories).filter(cat => cat.length > 0).length;
        
        Object.entries(categories).forEach(([category, categoryMemories]) => {
            if (categoryMemories.length > 0) {
                categoryCount++;
                const isLast = categoryCount === totalCategories;
                const categoryIcon = categoryInfo[category]?.icon || '📝';
                const categoryTitle = categoryInfo[category]?.title || 'Context';
                const categoryColor = categoryInfo[category]?.color || COLORS.GRAY;
                
                contextMessage += `${COLORS.CYAN}${isLast ? '└─' : '├─'}${COLORS.RESET} ${categoryIcon} ${categoryColor}${categoryTitle}${COLORS.RESET}:\n`;
                hasContent = true;
                
                categoryMemories.forEach((memory, idx) => {
                    const formatted = formatMemoryForCLI(memory, 0, {
                        maxContentLength: maxContentLengthCategorized,
                        includeDate: includeTimestamp,
                        indent: true
                    });
                    if (formatted) {
                        const isLastMemory = idx === categoryMemories.length - 1;
                        const connector = isLast ? ' ' : `${COLORS.CYAN}│${COLORS.RESET}`;
                        const prefix = isLastMemory 
                            ? `${connector}  ${COLORS.CYAN}└─${COLORS.RESET} ` 
                            : `${connector}  ${COLORS.CYAN}├─${COLORS.RESET} `;
                        contextMessage += `${prefix}${formatted}\n`;
                    }
                });
                if (!isLast) contextMessage += `${COLORS.CYAN}│${COLORS.RESET}\n`;
            }
        });
        
        if (!hasContent) {
            // Fallback to linear format
            validMemories.forEach(({ formatted }, idx) => {
                const isLast = idx === validMemories.length - 1;
                contextMessage += `${COLORS.CYAN}${isLast ? '└─' : '├─'}${COLORS.RESET} ${formatted}\n`;
            });
        }
    } else {
        // Simple linear formatting with enhanced visual elements
        validMemories.forEach(({ formatted }, idx) => {
            const isLast = idx === validMemories.length - 1;
            contextMessage += `${COLORS.CYAN}${isLast ? '└─' : '├─'}${COLORS.RESET} ${formatted}\n`;
        });
    }
    
    return contextMessage;
}

/**
 * Format individual memory for CLI with color coding
 */
function formatMemoryForCLI(memory, index, options = {}) {
    try {
        const {
            maxContentLength = 400,
            includeDate = true,
            indent = false
        } = options;
        
        // Extract meaningful content with markdown conversion enabled for CLI
        const content = extractMeaningfulContent(
            memory.content || 'No content available', 
            maxContentLength,
            { convertMarkdown: true, stripMarkdown: false }
        );
        
        // Skip generic summaries
        if (isGenericSessionSummary(memory.content)) {
            return null;
        }
        
        // Format date with recency indicators and color
        let dateStr = '';
        if (includeDate && memory.created_at_iso) {
            const date = new Date(memory.created_at_iso);
            const now = new Date();
            const daysDiff = (now - date) / (1000 * 60 * 60 * 24);
            
            let recencyIndicator = '';
            let dateColor = COLORS.GRAY;
            
            if (daysDiff < 1) {
                recencyIndicator = '🕒 ';
                dateColor = COLORS.GREEN;
                dateStr = ` ${dateColor}${recencyIndicator}today${COLORS.RESET}`;
            } else if (daysDiff < 2) {
                recencyIndicator = '📅 ';
                dateColor = COLORS.GREEN;
                dateStr = ` ${dateColor}${recencyIndicator}yesterday${COLORS.RESET}`;
            } else if (daysDiff <= 7) {
                recencyIndicator = '📅 ';
                dateColor = COLORS.CYAN;
                const formattedDate = date.toLocaleDateString('en-US', { weekday: 'short' });
                dateStr = ` ${dateColor}${recencyIndicator}${formattedDate}${COLORS.RESET}`;
            } else {
                const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                dateStr = ` ${COLORS.GRAY}(${formattedDate})${COLORS.RESET}`;
            }
        }
        
        // Color the content based on type
        let coloredContent = content;
        if (memory.memory_type === 'decision' || (memory.tags && memory.tags.some(tag => tag.includes('decision')))) {
            coloredContent = `${COLORS.YELLOW}${content}${COLORS.RESET}`;
        } else if (memory.memory_type === 'insight') {
            coloredContent = `${COLORS.MAGENTA}${content}${COLORS.RESET}`;
        } else if (memory.memory_type === 'bug-fix') {
            coloredContent = `${COLORS.GREEN}${content}${COLORS.RESET}`;
        } else if (memory.memory_type === 'feature') {
            coloredContent = `${COLORS.BLUE}${content}${COLORS.RESET}`;
        }
        
        return `${coloredContent}${dateStr}`;
        
    } catch (error) {
        return `${COLORS.GRAY}[Error formatting memory: ${error.message}]${COLORS.RESET}`;
    }
}

/**
 * Extract meaningful content from session summaries and structured memories
 */
function extractMeaningfulContent(content, maxLength = 500, options = {}) {
    if (!content || typeof content !== 'string') {
        return 'No content available';
    }
    
    const {
        convertMarkdown = isCLIEnvironment(),  // Auto-convert in CLI mode
        stripMarkdown = false  // Just strip without ANSI colors
    } = options;
    
    // Check if this is a session summary with structured sections
    if (content.includes('# Session Summary') || content.includes('## 🎯') || content.includes('## 🏛️') || content.includes('## 💡')) {
        const sections = {
            decisions: [],
            insights: [],
            codeChanges: [],
            nextSteps: [],
            topics: []
        };
        
        // Extract structured sections
        const lines = content.split('\n');
        let currentSection = null;
        
        for (const line of lines) {
            const trimmed = line.trim();
            
            if (trimmed.includes('🏛️') && trimmed.includes('Decision')) {
                currentSection = 'decisions';
                continue;
            } else if (trimmed.includes('💡') && (trimmed.includes('Insight') || trimmed.includes('Key'))) {
                currentSection = 'insights';
                continue;
            } else if (trimmed.includes('💻') && trimmed.includes('Code')) {
                currentSection = 'codeChanges';
                continue;
            } else if (trimmed.includes('📋') && trimmed.includes('Next')) {
                currentSection = 'nextSteps';
                continue;
            } else if (trimmed.includes('🎯') && trimmed.includes('Topic')) {
                currentSection = 'topics';
                continue;
            } else if (trimmed.startsWith('##') || trimmed.startsWith('#')) {
                currentSection = null; // Reset on new major section
                continue;
            }
            
            // Collect bullet points under current section
            if (currentSection && trimmed.startsWith('- ') && trimmed.length > 2) {
                const item = trimmed.substring(2).trim();
                if (item.length > 5 && item !== 'implementation' && item !== '...') {
                    sections[currentSection].push(item);
                }
            }
        }
        
        // Build meaningful summary from extracted sections
        const meaningfulParts = [];
        
        if (sections.decisions.length > 0) {
            meaningfulParts.push(`Decisions: ${sections.decisions.slice(0, 2).join('; ')}`);
        }
        if (sections.insights.length > 0) {
            meaningfulParts.push(`Insights: ${sections.insights.slice(0, 2).join('; ')}`);
        }
        if (sections.codeChanges.length > 0) {
            meaningfulParts.push(`Changes: ${sections.codeChanges.slice(0, 2).join('; ')}`);
        }
        if (sections.nextSteps.length > 0) {
            meaningfulParts.push(`Next: ${sections.nextSteps.slice(0, 2).join('; ')}`);
        }
        
        if (meaningfulParts.length > 0) {
            const extracted = meaningfulParts.join(' | ');
            const truncated = extracted.length > maxLength ? extracted.substring(0, maxLength - 3) + '...' : extracted;
            
            // Apply markdown conversion if requested
            if (convertMarkdown) {
                return convertMarkdownToANSI(truncated, { stripOnly: stripMarkdown });
            }
            return truncated;
        }
    }
    
    // For non-structured content, apply markdown conversion first if needed
    let processedContent = content;
    if (convertMarkdown) {
        processedContent = convertMarkdownToANSI(content, { stripOnly: stripMarkdown });
    }
    
    // Then use smart truncation
    if (processedContent.length <= maxLength) {
        return processedContent;
    }
    
    // Try to find a good breaking point (sentence, paragraph, or code block)
    const breakPoints = ['. ', '\n\n', '\n', '; '];
    
    for (const breakPoint of breakPoints) {
        const lastBreak = processedContent.lastIndexOf(breakPoint, maxLength - 3);
        if (lastBreak > maxLength * 0.7) { // Only use if we keep at least 70% of desired length
            return processedContent.substring(0, lastBreak + (breakPoint === '. ' ? 1 : 0)) + '...';
        }
    }
    
    // Fallback to hard truncation
    return processedContent.substring(0, maxLength - 3) + '...';
}

/**
 * Check if memory content appears to be a generic/empty session summary
 */
function isGenericSessionSummary(content) {
    if (!content || typeof content !== 'string') {
        return true;
    }
    
    // Check for generic patterns
    const genericPatterns = [
        /## 🎯 Topics Discussed\s*-\s*implementation\s*-\s*\.\.\.?$/m,
        /Topics Discussed.*implementation.*\.\.\..*$/s,
        /Session Summary.*implementation.*\.\.\..*$/s
    ];
    
    return genericPatterns.some(pattern => pattern.test(content));
}

/**
 * Format a single memory for context display
 */
function formatMemory(memory, index = 0, options = {}) {
    try {
        const {
            includeScore = false,
            includeMetadata = false,
            maxContentLength = 500,
            includeDate = true,
            showOnlyRelevantTags = true
        } = options;
        
        // Extract meaningful content using smart parsing
        // For non-CLI, strip markdown without adding ANSI colors
        const content = extractMeaningfulContent(
            memory.content || 'No content available', 
            maxContentLength,
            { convertMarkdown: true, stripMarkdown: true }
        );
        
        // Skip generic/empty session summaries
        if (isGenericSessionSummary(memory.content) && !includeScore) {
            return null; // Signal to skip this memory
        }
        
        // Format date more concisely
        let dateStr = '';
        if (includeDate && memory.created_at_iso) {
            const date = new Date(memory.created_at_iso);
            dateStr = ` (${date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })})`;
        }
        
        // Build formatted memory
        let formatted = `${index + 1}. ${content}${dateStr}`;
        
        // Add only the most relevant tags
        if (showOnlyRelevantTags && memory.tags && memory.tags.length > 0) {
            const relevantTags = memory.tags.filter(tag => {
                const tagLower = tag.toLowerCase();
                return !tagLower.startsWith('source:') && 
                       !tagLower.startsWith('claude-code-session') &&
                       !tagLower.startsWith('session-consolidation') &&
                       tagLower !== 'claude-code' &&
                       tagLower !== 'auto-generated' &&
                       tagLower !== 'implementation' &&
                       tagLower.length > 2;
            });
            
            // Only show tags if they add meaningful context (max 3)
            if (relevantTags.length > 0 && relevantTags.length <= 5) {
                formatted += `\n   Tags: ${relevantTags.slice(0, 3).join(', ')}`;
            }
        }
        
        return formatted;
        
    } catch (error) {
        // Silently fail with error message to avoid noise
        return `${index + 1}. [Error formatting memory: ${error.message}]`;
    }
}

/**
 * Deduplicate memories based on content similarity
 */
function deduplicateMemories(memories, options = {}) {
    if (!Array.isArray(memories) || memories.length <= 1) {
        return memories;
    }
    
    const deduplicated = [];
    const seenContent = new Set();
    
    // Sort by relevance score (highest first) and recency
    const sorted = memories.sort((a, b) => {
        const scoreA = a.relevanceScore || 0;
        const scoreB = b.relevanceScore || 0;
        if (scoreA !== scoreB) return scoreB - scoreA;
        
        // If scores are equal, prefer more recent
        const dateA = new Date(a.created_at_iso || 0);
        const dateB = new Date(b.created_at_iso || 0);
        return dateB - dateA;
    });
    
    for (const memory of sorted) {
        const content = memory.content || '';
        
        // Create a normalized version for comparison
        let normalized = content.toLowerCase()
            .replace(/# session summary.*?\n/gi, '') // Remove session headers
            .replace(/\*\*date\*\*:.*?\n/gi, '')    // Remove date lines
            .replace(/\*\*project\*\*:.*?\n/gi, '') // Remove project lines
            .replace(/\s+/g, ' ')                   // Normalize whitespace
            .trim();
        
        // Skip if content is too generic or already seen
        if (normalized.length < 20 || isGenericSessionSummary(content)) {
            continue;
        }
        
        // Check for substantial similarity
        let isDuplicate = false;
        for (const seenNormalized of seenContent) {
            const similarity = calculateContentSimilarity(normalized, seenNormalized);
            if (similarity > 0.8) { // 80% similarity threshold
                isDuplicate = true;
                break;
            }
        }
        
        if (!isDuplicate) {
            seenContent.add(normalized);
            deduplicated.push(memory);
        }
    }
    
    // Only log if in verbose mode (can be passed via options)
    if (options?.verbose !== false && memories.length !== deduplicated.length) {
        console.log(`[Context Formatter] Deduplicated ${memories.length} → ${deduplicated.length} memories`);
    }
    return deduplicated;
}

/**
 * Calculate content similarity between two normalized strings
 */
function calculateContentSimilarity(str1, str2) {
    if (!str1 || !str2) return 0;
    if (str1 === str2) return 1;
    
    // Use simple word overlap similarity
    const words1 = new Set(str1.split(/\s+/).filter(w => w.length > 3));
    const words2 = new Set(str2.split(/\s+/).filter(w => w.length > 3));
    
    if (words1.size === 0 && words2.size === 0) return 1;
    if (words1.size === 0 || words2.size === 0) return 0;
    
    const intersection = new Set([...words1].filter(w => words2.has(w)));
    const union = new Set([...words1, ...words2]);
    
    return intersection.size / union.size;
}

/**
 * Group memories by category for better organization
 */
function groupMemoriesByCategory(memories, options = {}) {
    try {
        // First deduplicate to remove redundant content
        const deduplicated = deduplicateMemories(memories, options);
        
        const categories = {
            gitContext: [],
            recent: [],
            decisions: [],
            architecture: [],
            insights: [],
            bugs: [],
            features: [],
            other: []
        };
        
        const now = new Date();
        
        deduplicated.forEach(memory => {
            const type = memory.memory_type?.toLowerCase() || 'other';
            const tags = memory.tags || [];
            
            // Check if memory is recent (within last week)
            let isRecent = false;
            if (memory.created_at_iso) {
                const memDate = new Date(memory.created_at_iso);
                const daysDiff = (now - memDate) / (1000 * 60 * 60 * 24);
                isRecent = daysDiff <= 7;
            }
            
            // Prioritize git context categorization (highest priority)
            if (memory._gitContextType) {
                categories.gitContext.push(memory);
            } else if (isRecent) {
                categories.recent.push(memory);
            } else if (type === 'decision' || tags.some(tag => tag.includes('decision'))) {
                categories.decisions.push(memory);
            } else if (type === 'architecture' || tags.some(tag => tag.includes('architecture'))) {
                categories.architecture.push(memory);
            } else if (type === 'insight' || tags.some(tag => tag.includes('insight'))) {
                categories.insights.push(memory);
            } else if (type === 'bug-fix' || tags.some(tag => tag.includes('bug'))) {
                categories.bugs.push(memory);
            } else if (type === 'feature' || tags.some(tag => tag.includes('feature'))) {
                categories.features.push(memory);
            } else {
                categories.other.push(memory);
            }
        });
        
        return categories;
        
    } catch (error) {
        if (options?.verbose !== false) {
            console.warn('[Context Formatter] Error grouping memories:', error.message);
        }
        return { other: memories };
    }
}

/**
 * Create a context summary from project information
 */
function createProjectSummary(projectContext) {
    try {
        let summary = `**Project**: ${projectContext.name}`;
        
        if (projectContext.language && projectContext.language !== 'Unknown') {
            summary += ` (${projectContext.language})`;
        }
        
        if (projectContext.frameworks && projectContext.frameworks.length > 0) {
            summary += `\n**Frameworks**: ${projectContext.frameworks.join(', ')}`;
        }
        
        if (projectContext.tools && projectContext.tools.length > 0) {
            summary += `\n**Tools**: ${projectContext.tools.join(', ')}`;
        }
        
        if (projectContext.git && projectContext.git.isRepo) {
            summary += `\n**Branch**: ${projectContext.git.branch || 'unknown'}`;
            
            if (projectContext.git.lastCommit) {
                summary += `\n**Last Commit**: ${projectContext.git.lastCommit}`;
            }
        }
        
        return summary;
        
    } catch (error) {
        // Silently fail with fallback summary
        return `**Project**: ${projectContext.name || 'Unknown Project'}`;
    }
}

/**
 * Format memories for Claude Code context injection
 */
function formatMemoriesForContext(memories, projectContext, options = {}) {
    try {
        // Use CLI formatting if in CLI environment
        if (isCLIEnvironment()) {
            return formatMemoriesForCLI(memories, projectContext, options);
        }
        
        const {
            includeProjectSummary = true,
            includeScore = false,
            groupByCategory = true,
            maxMemories = 8,
            includeTimestamp = true,
            maxContentLength = 500,
            storageInfo = null
        } = options;
        
        if (!memories || memories.length === 0) {
            return `## 📋 Memory Context\n\nNo relevant memories found for this session.\n`;
        }
        
        // Filter out null/generic memories and limit number
        const validMemories = [];
        let memoryIndex = 0;
        
        for (const memory of memories) {
            if (validMemories.length >= maxMemories) break;
            
            const formatted = formatMemory(memory, memoryIndex, {
                includeScore,
                maxContentLength: maxContentLength,
                includeDate: includeTimestamp,
                showOnlyRelevantTags: true
            });
            
            if (formatted) { // formatMemory returns null for generic summaries
                validMemories.push({ memory, formatted });
                memoryIndex++;
            }
        }
        
        if (validMemories.length === 0) {
            return `## 📋 Memory Context\n\nNo meaningful memories found for this session (filtered out generic content).\n`;
        }
        
        // Start building context message
        let contextMessage = '## 🧠 Memory Context Loaded\n\n';
        
        // Add project summary
        if (includeProjectSummary && projectContext) {
            contextMessage += createProjectSummary(projectContext) + '\n\n';
        }
        
        // Add storage information
        if (storageInfo) {
            contextMessage += `**Storage**: ${storageInfo.description}`;
            
            // Add health information if available
            if (storageInfo.health && storageInfo.health.totalMemories > 0) {
                const memoryCount = storageInfo.health.totalMemories;
                const dbSize = storageInfo.health.databaseSizeMB;
                const uniqueTags = storageInfo.health.uniqueTags;
                
                contextMessage += ` - ${memoryCount} memories`;
                if (dbSize > 0) contextMessage += `, ${dbSize}MB`;
                if (uniqueTags > 0) contextMessage += `, ${uniqueTags} unique tags`;
            }
            contextMessage += '\n';
            
            if (storageInfo.location && !storageInfo.location.includes('Configuration Error') && !storageInfo.location.includes('Health parse error')) {
                contextMessage += `**Location**: \`${storageInfo.location}\`\n`;
            }
            
            if (storageInfo.health && storageInfo.health.embeddingModel && storageInfo.health.embeddingModel !== 'Unknown') {
                contextMessage += `**Embedding Model**: ${storageInfo.health.embeddingModel}\n`;
            }
            
            contextMessage += '\n';
        }
        
        contextMessage += `**Loaded ${validMemories.length} relevant memories from your project history:**\n\n`;
        
        if (groupByCategory && validMemories.length > 3) {
            // Group and format by category only if we have enough content
            const categories = groupMemoriesByCategory(validMemories.map(v => v.memory));
            
            const categoryTitles = {
                gitContext: '### ⚡ Current Development (Git Context)',
                recent: '### 🕒 Recent Work (Last Week)',
                decisions: '### 🎯 Key Decisions',
                architecture: '### 🏗️ Architecture & Design', 
                insights: '### 💡 Insights & Learnings',
                bugs: '### 🐛 Bug Fixes & Issues',
                features: '### ✨ Features & Implementation',
                other: '### 📝 Additional Context'
            };
            
            let hasContent = false;
            Object.entries(categories).forEach(([category, categoryMemories]) => {
                if (categoryMemories.length > 0) {
                    contextMessage += `${categoryTitles[category]}\n`;
                    hasContent = true;
                    
                    categoryMemories.forEach((memory, index) => {
                        const formatted = formatMemory(memory, index, {
                            includeScore,
                            maxContentLength: maxContentLength,
                            includeDate: includeTimestamp,
                            showOnlyRelevantTags: true
                        });
                        if (formatted) {
                            contextMessage += `${formatted}\n\n`;
                        }
                    });
                }
            });
            
            if (!hasContent) {
                // Fallback to linear format
                validMemories.forEach(({ formatted }) => {
                    contextMessage += `${formatted}\n\n`;
                });
            }
            
        } else {
            // Simple linear formatting for small lists
            validMemories.forEach(({ formatted }) => {
                contextMessage += `${formatted}\n\n`;
            });
        }
        
        // Add concise footer
        contextMessage += '---\n';
        contextMessage += '*This context was automatically loaded based on your project and recent activities. ';
        contextMessage += 'Use this information to maintain continuity with your previous work and decisions.*';
        
        return contextMessage;
        
    } catch (error) {
        // Return error context without logging to avoid noise
        return `## 📋 Memory Context\n\n*Error loading context: ${error.message}*\n`;
    }
}

/**
 * Format memory for session-end consolidation
 */
function formatSessionConsolidation(sessionData, projectContext) {
    try {
        const timestamp = new Date().toISOString();
        
        let consolidation = `# Session Summary - ${projectContext.name}\n`;
        consolidation += `**Date**: ${new Date().toLocaleDateString()}\n`;
        consolidation += `**Project**: ${projectContext.name} (${projectContext.language})\n\n`;
        
        if (sessionData.topics && sessionData.topics.length > 0) {
            consolidation += `## 🎯 Topics Discussed\n`;
            sessionData.topics.forEach(topic => {
                consolidation += `- ${topic}\n`;
            });
            consolidation += '\n';
        }
        
        if (sessionData.decisions && sessionData.decisions.length > 0) {
            consolidation += `## 🏛️ Decisions Made\n`;
            sessionData.decisions.forEach(decision => {
                consolidation += `- ${decision}\n`;
            });
            consolidation += '\n';
        }
        
        if (sessionData.insights && sessionData.insights.length > 0) {
            consolidation += `## 💡 Key Insights\n`;
            sessionData.insights.forEach(insight => {
                consolidation += `- ${insight}\n`;
            });
            consolidation += '\n';
        }
        
        if (sessionData.codeChanges && sessionData.codeChanges.length > 0) {
            consolidation += `## 💻 Code Changes\n`;
            sessionData.codeChanges.forEach(change => {
                consolidation += `- ${change}\n`;
            });
            consolidation += '\n';
        }
        
        if (sessionData.nextSteps && sessionData.nextSteps.length > 0) {
            consolidation += `## 📋 Next Steps\n`;
            sessionData.nextSteps.forEach(step => {
                consolidation += `- ${step}\n`;
            });
            consolidation += '\n';
        }
        
        consolidation += `---\n*Session captured by Claude Code Memory Awareness at ${timestamp}*`;
        
        return consolidation;
        
    } catch (error) {
        // Return error without logging to avoid noise
        return `Session Summary Error: ${error.message}`;
    }
}

module.exports = {
    formatMemoriesForContext,
    formatMemoriesForCLI,
    formatMemory,
    formatMemoryForCLI,
    groupMemoriesByCategory,
    createProjectSummary,
    formatSessionConsolidation,
    isCLIEnvironment,
    convertMarkdownToANSI
};

// Direct execution support for testing
if (require.main === module) {
    // Test with mock data
    const mockMemories = [
        {
            content: 'Decided to use SQLite-vec for better performance, 10x faster than ChromaDB',
            tags: ['mcp-memory-service', 'decision', 'sqlite-vec', 'performance'],
            memory_type: 'decision',
            created_at_iso: '2025-08-19T10:00:00Z',
            relevanceScore: 0.95
        },
        {
            content: 'Implemented Claude Code hooks system for automatic memory awareness. Created session-start, session-end, and topic-change hooks.',
            tags: ['claude-code', 'hooks', 'architecture', 'memory-awareness'],
            memory_type: 'architecture',
            created_at_iso: '2025-08-19T09:30:00Z',
            relevanceScore: 0.87
        },
        {
            content: 'Fixed critical bug in project detector - was not handling pyproject.toml files correctly',
            tags: ['bug-fix', 'project-detector', 'python'],
            memory_type: 'bug-fix',
            created_at_iso: '2025-08-18T15:30:00Z',
            relevanceScore: 0.72
        },
        {
            content: 'Added new feature: Claude Code hooks with session lifecycle management',
            tags: ['feature', 'claude-code', 'hooks'],
            memory_type: 'feature',
            created_at_iso: '2025-08-17T12:00:00Z',
            relevanceScore: 0.85
        },
        {
            content: 'Key insight: Memory deduplication prevents information overload in context',
            tags: ['insight', 'memory-management', 'optimization'],
            memory_type: 'insight',
            created_at_iso: '2025-08-16T14:00:00Z',
            relevanceScore: 0.78
        }
    ];
    
    const mockProjectContext = {
        name: 'mcp-memory-service',
        language: 'JavaScript',
        frameworks: ['Node.js'],
        tools: ['npm'],
        branch: 'main',
        lastCommit: 'cdabc9a feat: enhance deduplication script'
    };
    
    console.log('\n=== CONTEXT FORMATTING TEST ===');
    const formatted = formatMemoriesForContext(mockMemories, mockProjectContext, {
        includeScore: true,
        groupByCategory: true
    });
    
    console.log(formatted);
    console.log('\n=== END TEST ===');
}