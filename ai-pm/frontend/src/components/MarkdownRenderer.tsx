import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import './MarkdownRenderer.css';
import './MarkdownRenderer.css';

interface MarkdownRendererProps {
  content: string;
  className?: string;
  fallbackText?: string;
}

export default function MarkdownRenderer({ 
  content, 
  className = '', 
  fallbackText = 'No content provided.' 
}: MarkdownRendererProps) {
  // If content is empty or only whitespace, show fallback
  if (!content || !content.trim()) {
    return <div className={`text-gray-500 italic ${className}`}>{fallbackText}</div>;
  }

  return (
    <div className={`markdown-renderer ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headers
          h1: ({ node, ...props }) => (
            <h1 className="text-xl font-bold text-gray-900 mt-6 mb-4 first:mt-0" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-lg font-semibold text-gray-900 mt-5 mb-3 first:mt-0" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-base font-semibold text-gray-900 mt-4 mb-2 first:mt-0" {...props} />
          ),
          h4: ({ node, ...props }) => (
            <h4 className="text-sm font-semibold text-gray-900 mt-3 mb-2 first:mt-0" {...props} />
          ),
          h5: ({ node, ...props }) => (
            <h5 className="text-sm font-medium text-gray-900 mt-3 mb-1 first:mt-0" {...props} />
          ),
          h6: ({ node, ...props }) => (
            <h6 className="text-xs font-medium text-gray-700 mt-2 mb-1 first:mt-0" {...props} />
          ),
          
          // Paragraphs
          p: ({ node, ...props }) => (
            <p className="text-gray-700 mb-3 last:mb-0 leading-relaxed break-words" {...props} />
          ),
          
          // Lists
          ul: ({ node, ...props }) => (
            <ul className="list-disc list-inside mb-3 space-y-1 text-gray-700" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal list-inside mb-3 space-y-1 text-gray-700" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="leading-relaxed" {...props} />
          ),
          
          // Code
          code: ({ className, children }: any) => {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            const isInline = !match;
            
            if (isInline) {
              return (
                <code className="markdown-inline-code">
                  {children}
                </code>
              );
            }
            
            // For code blocks, use SyntaxHighlighter with proper containment
            return (
              <div className="markdown-code-container">
                <SyntaxHighlighter
                  style={oneDark}
                  language={language || 'text'}
                  PreTag="div"
                  customStyle={{
                    margin: 0,
                    padding: '1rem',
                    fontSize: '14px',
                    lineHeight: '1.4',
                    borderRadius: '0.5rem',
                    border: 'none',
                    background: 'transparent',
                  }}
                  wrapLongLines={false}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              </div>
            );
          },
          pre: ({ children }) => (
            <div className="markdown-pre-block">
              <pre>
                {children}
              </pre>
            </div>
          ),
          
          // Blockquotes
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-600 my-3" {...props} />
          ),
          
          // Links
          a: ({ node, ...props }) => (
            <a className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer" {...props} />
          ),
          
          // Strong/Bold
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-gray-900" {...props} />
          ),
          
          // Emphasis/Italic
          em: ({ node, ...props }) => (
            <em className="italic" {...props} />
          ),
          
          // Horizontal rule
          hr: ({ node, ...props }) => (
            <hr className="border-t border-gray-300 my-6" {...props} />
          ),
          
          // Tables (GitHub Flavored Markdown)
          table: ({ node, ...props }) => (
            <div className="markdown-table-container">
              <table className="markdown-table" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-gray-50" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th {...props} />
          ),
          td: ({ node, ...props }) => (
            <td {...props} />
          ),
          
          // Strikethrough (GitHub Flavored Markdown)
          del: ({ node, ...props }) => (
            <del className="line-through text-gray-500" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
