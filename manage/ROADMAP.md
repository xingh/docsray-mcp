# Docsray MCP Framework Specification

## Executive Summary

Docsray is a modular Model Context Protocol (MCP) framework for advanced document perception and understanding. It provides a unified interface for multiple document processing backends including pymupdf4llm, pytesseract, ocrmypdf, mistral-ocr, and llama-parse, exposed through standardized MCP tool endpoints. The framework supports both SSE and HTTP transport modes, handles diverse document formats, and enables intelligent provider selection based on document characteristics and processing requirements.

## 1. System Architecture Overview

### 1.1 Core Architecture Components

```
┌────────────────────────────────────────────────────────────┐
│                     MCP Host (Claude/IDE)                  │
└───────────────────────────┬────────────────────────────────┘
                            │ MCP Protocol
┌───────────────────────────┴────────────────────────────────┐
│                    Docsray MCP Server                      │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Transport Layer (HTTP/SSE)             │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           MCP Protocol Handler (JSON-RPC)           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                Tool Registry & Router               │   │
│  │  ├─ seek    ├─ peek    ├─ map                       │   │
│  │  ├─ xray    └─ extract                              │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Provider Abstraction Layer             │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Provider Registry                   │   │
│  │  ├─ PyMuPDF4LLM  ├─ PyTesseract  ├─ OCRmyPDF        │   │
│  │  ├─ MistralOCR   └─ LlamaParse                      │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### 1.2 Key Design Principles

- **Provider Agnostic**: Core functionality independent of specific document processing implementations
- **Graceful Degradation**: Automatic fallback between providers based on capability and availability
- **Format Intelligence**: Smart provider selection based on document type and requirements
- **Performance Optimized**: Caching, connection pooling, and parallel processing support
- **Error Resilient**: Comprehensive error handling with circuit breakers and retry logic

## 2. MCP Server Implementation

### 2.1 Server Initialization and Configuration

```typescript
interface DocsrayConfig {
  // Transport configuration
  transport: {
    type: 'stdio' | 'http';
    httpPort?: number;
    httpHost?: string;
  };
  
  // Provider configuration
  providers: {
    pymupdf4llm?: {
      enabled: boolean;
      config?: PyMuPDFConfig;
    };
    pytesseract?: {
      enabled: boolean;
      tesseractPath?: string;
      languages?: string[];
    };
    ocrmypdf?: {
      enabled: boolean;
      config?: OCRmyPDFConfig;
    };
    mistralOcr?: {
      enabled: boolean;
      apiKey: string;
      baseUrl?: string;
    };
    llamaParse?: {
      enabled: boolean;
      apiKey: string;
      parsingMode?: 'fast' | 'balanced' | 'premium';
    };
  };
  
  // Performance settings
  performance: {
    cacheEnabled: boolean;
    cacheTTL: number;
    maxConcurrentRequests: number;
    timeoutSeconds: number;
  };
}
```

### 2.2 MCP Protocol Implementation

**Version Negotiation and Capability Exchange:**
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "tools": {},
      "resources": {
        "subscribe": false,
        "templates": true
      }
    },
    "clientInfo": {
      "name": "docsray",
      "version": "1.0.0"
    }
  }
}
```

**Server Capabilities Response:**
```json
{
  "protocolVersion": "2025-03-26",
  "capabilities": {
    "tools": {},
    "resources": {
      "subscribe": false,
      "templates": true
    }
  },
  "serverInfo": {
    "name": "docsray",
    "version": "1.0.0"
  }
}
```

## 3. Tool Endpoint Specifications

### 3.1 Seek Endpoint

**Purpose**: Navigate to specific pages or sections within documents

**Tool Definition:**
```typescript
{
  name: "docsray_seek",
  description: "Navigate to specific pages or sections in a document",
  inputSchema: {
    type: "object",
    properties: {
      documentUrl: {
        type: "string",
        description: "URL or path to the document"
      },
      target: {
        oneOf: [
          {
            type: "object",
            properties: {
              page: { type: "integer", minimum: 1 }
            }
          },
          {
            type: "object",
            properties: {
              section: { type: "string" }
            }
          },
          {
            type: "object",
            properties: {
              query: { type: "string" }
            }
          }
        ]
      },
      extractContent: {
        type: "boolean",
        default: true,
        description: "Whether to extract content from the target location"
      },
      provider: {
        type: "string",
        enum: ["auto", "pymupdf4llm", "ocrmypdf", "mistral-ocr", "llama-parse"],
        default: "auto"
      }
    },
    required: ["documentUrl", "target"]
  }
}
```

**Implementation Logic:**
1. Load document using appropriate provider
2. Navigate to specified location (page, section, or text search)
3. Extract content if requested
4. Return navigation result with context

### 3.2 Peek Endpoint

**Purpose**: Get document structure and overview without full extraction

**Tool Definition:**
```typescript
{
  name: "docsray_peek",
  description: "Get document structure, metadata, and overview",
  inputSchema: {
    type: "object",
    properties: {
      documentUrl: {
        type: "string",
        description: "URL or path to the document"
      },
      depth: {
        type: "string",
        enum: ["metadata", "structure", "preview"],
        default: "structure",
        description: "Level of detail to retrieve"
      },
      provider: {
        type: "string",
        enum: ["auto", "pymupdf4llm", "ocrmypdf", "mistral-ocr", "llama-parse"],
        default: "auto"
      }
    },
    required: ["documentUrl"]
  }
}
```

**Response Structure:**
```json
{
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "pageCount": 42,
    "format": "PDF",
    "fileSize": 1048576,
    "createdDate": "2024-01-01T00:00:00Z"
  },
  "structure": {
    "sections": [
      {
        "title": "Chapter 1",
        "page": 1,
        "subsections": []
      }
    ],
    "hasImages": true,
    "hasTables": true,
    "languages": ["en", "fr"]
  },
  "preview": {
    "firstPageText": "Preview text...",
    "tableOfContents": []
  }
}
```

### 3.3 Map Endpoint

**Purpose**: Generate comprehensive document structure map

**Tool Definition:**
```typescript
{
  name: "docsray_map",
  description: "Generate comprehensive document structure map",
  inputSchema: {
    type: "object",
    properties: {
      documentUrl: {
        type: "string",
        description: "URL or path to the document"
      },
      includeContent: {
        type: "boolean",
        default: false,
        description: "Include content snippets in the map"
      },
      analysisDepth: {
        type: "string",
        enum: ["shallow", "deep", "comprehensive"],
        default: "deep"
      },
      provider: {
        type: "string",
        enum: ["auto", "pymupdf4llm", "mistral-ocr", "llama-parse"],
        default: "auto"
      }
    },
    required: ["documentUrl"]
  }
}
```

**Map Output Structure:**
```json
{
  "documentMap": {
    "hierarchy": {
      "root": {
        "type": "document",
        "title": "Document Title",
        "children": [
          {
            "type": "section",
            "title": "Introduction",
            "page": 1,
            "children": []
          }
        ]
      }
    },
    "resources": {
      "images": [
        {
          "id": "img-001",
          "page": 5,
          "caption": "Figure 1",
          "coordinates": {}
        }
      ],
      "tables": [
        {
          "id": "table-001",
          "page": 7,
          "title": "Table 1",
          "dimensions": {"rows": 10, "columns": 5}
        }
      ]
    },
    "crossReferences": []
  }
}
```

### 3.4 Xray Endpoint

**Purpose**: Deep content analysis and extraction with AI-powered understanding

**Tool Definition:**
```typescript
{
  name: "docsray_xray",
  description: "Perform deep AI-powered document analysis",
  inputSchema: {
    type: "object",
    properties: {
      documentUrl: {
        type: "string",
        description: "URL or path to the document"
      },
      analysisType: {
        type: "array",
        items: {
          type: "string",
          enum: ["entities", "relationships", "key-points", "sentiment", "structure"]
        },
        default: ["entities", "key-points"]
      },
      customInstructions: {
        type: "string",
        description: "Custom analysis instructions (for compatible providers)"
      },
      provider: {
        type: "string",
        enum: ["mistral-ocr", "llama-parse"],
        default: "llama-parse"
      }
    },
    required: ["documentUrl"]
  }
}
```

### 3.5 Extract Endpoint

**Purpose**: Extract specific data types or content from documents

**Tool Definition:**
```typescript
{
  name: "docsray_extract",
  description: "Extract specific content or data from documents",
  inputSchema: {
    type: "object",
    properties: {
      documentUrl: {
        type: "string",
        description: "URL or path to the document"
      },
      extractionTargets: {
        type: "array",
        items: {
          type: "string",
          enum: ["text", "tables", "images", "forms", "metadata", "equations"]
        },
        default: ["text"]
      },
      outputFormat: {
        type: "string",
        enum: ["markdown", "json", "structured"],
        default: "markdown"
      },
      pages: {
        type: "array",
        items: { type: "integer" },
        description: "Specific pages to extract from"
      },
      provider: {
        type: "string",
        enum: ["auto", "pymupdf4llm", "pytesseract", "ocrmypdf", "mistral-ocr", "llama-parse"],
        default: "auto"
      }
    },
    required: ["documentUrl", "extractionTargets"]
  }
}
```

## 4. Provider Integration Layer

### 4.1 Provider Interface

```typescript
interface DocumentProvider {
  // Metadata
  getName(): string;
  getSupportedFormats(): string[];
  getCapabilities(): ProviderCapabilities;
  
  // Core operations
  canProcess(document: Document): Promise<boolean>;
  peek(document: Document, options: PeekOptions): Promise<PeekResult>;
  map(document: Document, options: MapOptions): Promise<DocumentMap>;
  seek(document: Document, target: SeekTarget): Promise<SeekResult>;
  xray(document: Document, options: XrayOptions): Promise<XrayResult>;
  extract(document: Document, options: ExtractOptions): Promise<ExtractResult>;
  
  // Lifecycle
  initialize(config: ProviderConfig): Promise<void>;
  dispose(): Promise<void>;
}

interface ProviderCapabilities {
  formats: string[];
  features: {
    ocr: boolean;
    tables: boolean;
    images: boolean;
    forms: boolean;
    multiLanguage: boolean;
    streaming: boolean;
    customInstructions: boolean;
  };
  performance: {
    maxFileSize: number;
    averageSpeed: number; // pages per second
  };
}
```

### 4.2 Provider-Specific Implementations

**PyMuPDF4LLM Provider:**
```typescript
class PyMuPDF4LLMProvider implements DocumentProvider {
  capabilities = {
    formats: ['pdf', 'xps', 'epub', 'cbz'],
    features: {
      ocr: false,
      tables: true,
      images: true,
      forms: true,
      multiLanguage: true,
      streaming: true,
      customInstructions: false
    },
    performance: {
      maxFileSize: 500 * 1024 * 1024, // 500MB
      averageSpeed: 100 // pages per second
    }
  };
  
  async extract(document: Document, options: ExtractOptions) {
    // Use pymupdf4llm's to_markdown with page_chunks
    const chunks = await pymupdf4llm.to_markdown(document.path, {
      page_chunks: true,
      write_images: options.extractionTargets.includes('images'),
      extract_words: true
    });
    
    return this.formatExtractResult(chunks, options.outputFormat);
  }
}
```

**Mistral OCR Provider:**
```typescript
class MistralOCRProvider implements DocumentProvider {
  capabilities = {
    formats: ['pdf', 'png', 'jpg', 'pptx', 'docx'],
    features: {
      ocr: true,
      tables: true,
      images: true,
      forms: false,
      multiLanguage: true,
      streaming: false,
      customInstructions: true
    },
    performance: {
      maxFileSize: 50 * 1024 * 1024, // 50MB
      averageSpeed: 2000 // pages per minute
    }
  };
  
  async xray(document: Document, options: XrayOptions) {
    // Use Mistral's document-as-prompt feature
    const response = await this.mistralClient.ocr.process({
      model: "mistral-ocr-latest",
      document: { type: "document_url", document_url: document.url },
      include_image_base64: true
    });
    
    // Apply AI analysis on extracted content
    return this.analyzeContent(response, options.analysisType);
  }
}
```

### 4.3 Provider Selection Algorithm

```typescript
class ProviderSelector {
  selectProvider(
    document: Document,
    operation: string,
    userPreference?: string
  ): DocumentProvider {
    // User preference takes precedence
    if (userPreference && userPreference !== 'auto') {
      const provider = this.registry.getProvider(userPreference);
      if (provider && provider.canProcess(document)) {
        return provider;
      }
    }
    
    // Score providers based on capability match
    const candidates = this.registry.getAllProviders()
      .filter(p => p.canProcess(document))
      .map(p => ({
        provider: p,
        score: this.scoreProvider(p, document, operation)
      }))
      .sort((a, b) => b.score - a.score);
    
    if (candidates.length === 0) {
      throw new Error(`No provider available for ${document.format}`);
    }
    
    return candidates[0].provider;
  }
  
  private scoreProvider(
    provider: DocumentProvider,
    document: Document,
    operation: string
  ): number {
    let score = 0;
    
    // Format compatibility
    if (provider.getSupportedFormats().includes(document.format)) {
      score += 10;
    }
    
    // Operation-specific scoring
    switch (operation) {
      case 'xray':
        if (provider.getCapabilities().features.customInstructions) {
          score += 5;
        }
        break;
      case 'extract':
        if (document.hasScannedContent && provider.getCapabilities().features.ocr) {
          score += 8;
        }
        break;
    }
    
    // Performance scoring
    if (document.size > 10 * 1024 * 1024) { // Large files
      score += provider.getCapabilities().performance.averageSpeed / 100;
    }
    
    return score;
  }
}
```

## 5. Transport Layer Implementation

### 5.1 HTTP Transport with SSE Support

```typescript
class HTTPTransport implements Transport {
  private app: Express;
  private sessions: Map<string, Session> = new Map();
  
  async start(config: TransportConfig) {
    this.app = express();
    this.app.use(express.json());
    
    // Main MCP endpoint
    this.app.all('/mcp', async (req, res) => {
      const sessionId = req.headers['mcp-session-id'] as string;
      
      if (req.method === 'GET') {
        // SSE connection for server-to-client messages
        this.handleSSE(req, res, sessionId);
      } else if (req.method === 'POST') {
        // JSON-RPC request handling
        await this.handleRequest(req, res, sessionId);
      }
    });
    
    this.app.listen(config.port, config.host);
  }
  
  private async handleRequest(req: Request, res: Response, sessionId?: string) {
    const request = req.body;
    
    // Initialize session if needed
    if (request.method === 'initialize') {
      sessionId = this.generateSessionId();
      res.setHeader('Mcp-Session-Id', sessionId);
      this.sessions.set(sessionId, new Session());
    }
    
    try {
      const result = await this.server.handleRequest(request);
      res.json(result);
    } catch (error) {
      res.json(this.createErrorResponse(request.id, error));
    }
  }
  
  private handleSSE(req: Request, res: Response, sessionId: string) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    const session = this.sessions.get(sessionId);
    if (!session) {
      res.status(404).end();
      return;
    }
    
    // Send queued notifications
    session.on('notification', (notification) => {
      res.write(`data: ${JSON.stringify(notification)}\n\n`);
    });
  }
}
```

### 5.2 Standard I/O Transport

```typescript
class StdioTransport implements Transport {
  async start() {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    rl.on('line', async (line) => {
      try {
        const request = JSON.parse(line);
        const response = await this.server.handleRequest(request);
        console.log(JSON.stringify(response));
      } catch (error) {
        const errorResponse = this.createErrorResponse(null, error);
        console.log(JSON.stringify(errorResponse));
      }
    });
  }
}
```

## 6. Error Handling and Compatibility

### 6.1 Error Response Format

```typescript
interface DocsrayError {
  code: number;
  message: string;
  data?: {
    provider?: string;
    operation?: string;
    documentFormat?: string;
    fallbackProviders?: string[];
    details?: any;
  };
}

// Custom error codes
const ErrorCodes = {
  // Provider errors (-30xxx)
  PROVIDER_NOT_AVAILABLE: -30001,
  PROVIDER_INITIALIZATION_FAILED: -30002,
  NO_SUITABLE_PROVIDER: -30003,
  
  // Document errors (-31xxx)
  UNSUPPORTED_FORMAT: -31001,
  DOCUMENT_TOO_LARGE: -31002,
  DOCUMENT_CORRUPTED: -31003,
  DOCUMENT_ENCRYPTED: -31004,
  
  // Operation errors (-32xxx)
  OPERATION_TIMEOUT: -32001,
  OPERATION_FAILED: -32002,
  INVALID_TARGET: -32003
};
```

### 6.2 Compatibility Warnings

```typescript
class CompatibilityChecker {
  checkCompatibility(
    document: Document,
    provider: DocumentProvider,
    operation: string
  ): CompatibilityResult {
    const warnings: string[] = [];
    const errors: string[] = [];
    
    // Format compatibility
    if (!provider.getSupportedFormats().includes(document.format)) {
      errors.push(`Provider ${provider.getName()} does not support ${document.format}`);
    }
    
    // Size limits
    const maxSize = provider.getCapabilities().performance.maxFileSize;
    if (document.size > maxSize) {
      errors.push(`Document exceeds provider size limit (${maxSize} bytes)`);
    }
    
    // Feature compatibility
    if (operation === 'xray' && !provider.getCapabilities().features.customInstructions) {
      warnings.push('Provider does not support custom instructions for xray analysis');
    }
    
    // OCR requirements
    if (document.hasScannedContent && !provider.getCapabilities().features.ocr) {
      warnings.push('Document contains scanned content but provider lacks OCR capability');
    }
    
    return {
      compatible: errors.length === 0,
      warnings,
      errors,
      alternativeProviders: this.findAlternatives(document, operation)
    };
  }
}
```

### 6.3 Fallback Strategy

```typescript
class FallbackManager {
  private circuitBreakers: Map<string, CircuitBreaker> = new Map();
  
  async executeWithFallback<T>(
    operation: () => Promise<T>,
    fallbacks: Array<() => Promise<T>>
  ): Promise<T> {
    try {
      return await operation();
    } catch (primaryError) {
      for (const fallback of fallbacks) {
        try {
          return await fallback();
        } catch (fallbackError) {
          continue;
        }
      }
      throw new AggregateError([primaryError], 'All providers failed');
    }
  }
}
```

## 7. Performance Optimization

### 7.1 Caching Strategy

```typescript
interface CacheEntry {
  key: string;
  value: any;
  metadata: {
    provider: string;
    operation: string;
    timestamp: number;
    accessCount: number;
  };
}

class DocumentCache {
  private cache: LRUCache<string, CacheEntry>;
  
  generateKey(document: Document, operation: string, options: any): string {
    const normalized = {
      url: document.url,
      hash: document.hash,
      operation,
      options: this.normalizeOptions(options)
    };
    return crypto.createHash('sha256')
      .update(JSON.stringify(normalized))
      .digest('hex');
  }
  
  async get(key: string): Promise<any> {
    const entry = this.cache.get(key);
    if (entry && !this.isExpired(entry)) {
      entry.metadata.accessCount++;
      return entry.value;
    }
    return null;
  }
}
```

### 7.2 Connection Pooling

```typescript
class ProviderConnectionPool {
  private pools: Map<string, Pool> = new Map();
  
  getConnection(provider: string): PooledConnection {
    if (!this.pools.has(provider)) {
      this.pools.set(provider, this.createPool(provider));
    }
    return this.pools.get(provider).acquire();
  }
  
  private createPool(provider: string): Pool {
    return new Pool({
      create: () => this.createProviderInstance(provider),
      destroy: (instance) => instance.dispose(),
      min: 2,
      max: 10,
      idleTimeoutMillis: 30000
    });
  }
}
```

## 8. Command-Line Interface

### 8.1 CLI Structure

```bash
docsray [options] <command>

Commands:
  start              Start the MCP server
  test               Test provider connectivity
  list-providers     List available providers

Options:
  --config <path>    Configuration file path
  --transport <type> Transport type (stdio|http)
  --port <port>      HTTP port (default: 3000)
  --provider <name>  Default provider selection
  --verbose          Enable verbose logging
```

### 8.2 Provider Selection via CLI

```bash
# Start with specific provider
docsray start --provider mistral-ocr

# Start with multiple providers enabled
docsray start --enable-providers pymupdf4llm,ocrmypdf,mistral-ocr

# Test provider configuration
docsray test --provider llama-parse --document sample.pdf
```

## 9. Security Considerations

### 9.1 Input Validation

- Validate all document URLs and paths
- Implement file size limits
- Check file format magic bytes
- Sanitize custom instructions for AI providers
- Validate page numbers and ranges

### 9.2 API Security

- Rate limiting per session/client
- API key validation for external providers
- Secure credential storage
- Request signing for HTTP transport
- Origin validation for web-based clients

## 10. Implementation Roadmap

### Phase 1: Core Framework ✅ COMPLETE
- ✅ MCP server implementation (working in Cursor and other MCP clients)
- ✅ Basic provider interface
- ✅ PyMuPDF4LLM integration
- ✅ All five tool endpoints (seek, peek, map, xray, extract)
- ✅ Support for both URLs and local file paths (absolute, relative, home directory)

### Phase 2: Provider Expansion ✅ COMPLETE
- ❌ OCRmyPDF integration (deferred)
- ❌ Mistral OCR integration (deferred)
- ✅ LlamaParse support (fully implemented)
- ✅ Provider selection algorithm (auto-selection based on document characteristics)
- ✅ Compatibility checking (provider capability validation)

### Phase 3: Advanced Features ✅ COMPLETE
- ✅ Xray AI analysis endpoint (comprehensive entity extraction and analysis)
- ✅ Caching and performance optimization (comprehensive .docsray caching system)
- ✅ Circuit breakers and fallback logic (automatic PyMuPDF4LLM fallback)
- ✅ Comprehensive error handling (robust error handling across all tools)

### Phase 4: Production Readiness ✅ COMPLETE
- ✅ Security hardening (input validation, file size limits, path validation)
- ✅ Monitoring and metrics (performance tracking, cache statistics)
- ✅ Documentation and examples (comprehensive documentation website)
- ❌ Provider plugin SDK (future enhancement)

### Phase 5: Documentation (NEW) ✅ COMPLETE
- ✅ Complete documentation website with 20 comprehensive documentation files
- ✅ Getting Started guides (installation, quickstart, configuration)
- ✅ Provider documentation (overview, LlamaParse, PyMuPDF4LLM, comparison)
- ✅ Tools documentation (peek, map, xray, extract, seek)
- ✅ Examples (basic extraction, entity recognition, table extraction, custom instructions)
- ✅ Advanced guides (caching, performance optimization, troubleshooting)
- ✅ API reference (tools, providers, configuration)

## Conclusion

The Docsray MCP framework provides a powerful, extensible solution for document processing that leverages the best features of multiple document processing libraries and APIs. By following MCP protocol standards and implementing intelligent provider selection, comprehensive error handling, and performance optimizations, Docsray enables reliable, high-quality document understanding capabilities for AI applications.