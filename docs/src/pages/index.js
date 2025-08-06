import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Get Started - 5min ⏱️
          </Link>
          <Link
            className="button button--secondary button--lg margin-left--md"
            to="/docs/examples/comprehensive-extraction">
            See Maximum Extraction Demo 🚀
          </Link>
        </div>
        <div className={styles.quickExample}>
          <pre>
            <code className="language-bash">
{`# Install
pip install docsray-mcp

# Extract EVERYTHING from a document
mcp docsray xray document.pdf --provider llama-parse --comprehensive`}
            </code>
          </pre>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Advanced Document Perception for Claude`}
      description="Extract everything from any document - tables, images, entities, layouts, and more with AI-powered analysis">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
        
        <section className={styles.providerComparison}>
          <div className="container">
            <h2>Choose Your Provider</h2>
            <table className="provider-comparison-table">
              <thead>
                <tr>
                  <th>Provider</th>
                  <th>Speed</th>
                  <th>Capabilities</th>
                  <th>Best For</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>LlamaParse</strong> 🧠</td>
                  <td>5-30s</td>
                  <td>AI analysis, entities, tables, images, layouts, custom instructions</td>
                  <td>Comprehensive extraction, deep analysis</td>
                </tr>
                <tr>
                  <td><strong>PyMuPDF</strong> ⚡</td>
                  <td>&lt;1s</td>
                  <td>Text, basic markdown, fast extraction</td>
                  <td>Quick text retrieval, simple documents</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section className={styles.extractionDemo}>
          <div className="container">
            <h2>Maximum Data Extraction</h2>
            <div className="extraction-demo">
              <h3>Get EVERYTHING with one command:</h3>
              <pre>
                <code className="language-python">
{`# The ultimate extraction prompt for LlamaParse
result = docsray.xray(
    "document.pdf",
    provider="llama-parse",
    custom_instructions="""
    Extract ALL possible information including:
    1) Complete text content preserving exact formatting
    2) All tables with complete data and structure
    3) All images with descriptions and metadata
    4) Complete document metadata
    5) Full document structure with all sections
    6) All form fields and values
    7) All hyperlinks and cross-references
    8) All mathematical equations
    9) Page-by-page layout information
    10) All entity recognition (people, orgs, dates, amounts)
    """
)

# Returns EVERYTHING in result['full_extraction']`}
                </code>
              </pre>
            </div>
          </div>
        </section>

        <section className={styles.tools}>
          <div className="container">
            <h2>Five Powerful Tools</h2>
            <div className="row">
              <div className="col col--4">
                <div className="card">
                  <div className="card__header">
                    <h3>🔍 Peek</h3>
                  </div>
                  <div className="card__body">
                    <p>Quick overview, metadata, available formats</p>
                  </div>
                </div>
              </div>
              <div className="col col--4">
                <div className="card">
                  <div className="card__header">
                    <h3>🗺️ Map</h3>
                  </div>
                  <div className="card__body">
                    <p>Complete document structure and hierarchy</p>
                  </div>
                </div>
              </div>
              <div className="col col--4">
                <div className="card">
                  <div className="card__header">
                    <h3>🩻 Xray</h3>
                  </div>
                  <div className="card__body">
                    <p>Deep AI analysis, entities, comprehensive extraction</p>
                  </div>
                </div>
              </div>
              <div className="col col--4">
                <div className="card">
                  <div className="card__header">
                    <h3>📝 Extract</h3>
                  </div>
                  <div className="card__body">
                    <p>Get content in markdown, JSON, or text</p>
                  </div>
                </div>
              </div>
              <div className="col col--4">
                <div className="card">
                  <div className="card__header">
                    <h3>🎯 Seek</h3>
                  </div>
                  <div className="card__body">
                    <p>Navigate to specific pages or sections</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}