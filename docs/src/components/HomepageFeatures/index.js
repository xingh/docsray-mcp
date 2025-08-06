import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Comprehensive Extraction',
    icon: '🎯',
    description: (
      <>
        Extract EVERYTHING from documents - text, tables, images, entities, 
        layouts, metadata, and more with a single command using AI-powered analysis.
      </>
    ),
  },
  {
    title: 'Multi-Provider Support',
    icon: '🔄',
    description: (
      <>
        Choose between LlamaParse for deep AI analysis or PyMuPDF for lightning-fast 
        extraction. Auto-selection picks the best provider for your needs.
      </>
    ),
  },
  {
    title: 'Intelligent Caching',
    icon: '⚡',
    description: (
      <>
        All extractions are cached locally for instant retrieval. Process once, 
        access instantly forever. Smart invalidation when documents change.
      </>
    ),
  },
  {
    title: 'MCP Native',
    icon: '🤖',
    description: (
      <>
        Built specifically for Claude and MCP ecosystem. Five powerful tools 
        that work seamlessly with natural language prompts.
      </>
    ),
  },
  {
    title: 'Production Ready',
    icon: '✅',
    description: (
      <>
        52+ passing tests, comprehensive error handling, timeout protection, 
        and battle-tested with real-world documents.
      </>
    ),
  },
  {
    title: 'Universal Format Support',
    icon: '📄',
    description: (
      <>
        PDF, DOCX, PPTX, XLSX, HTML, Markdown, and more. Works with local files 
        and URLs. Handles everything from invoices to research papers.
      </>
    ),
  },
];

function Feature({icon, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <div className={styles.featureIcon}>{icon}</div>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}