# Docsray Documentation

This directory contains the Docusaurus-based documentation site for Docsray MCP.

## Development

### Install dependencies

```bash
npm install
```

### Start development server

```bash
npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

### Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Deployment

Using GitHub Pages:

```bash
GIT_USER=<Your GitHub username> npm run deploy
```

Using Vercel:

```bash
vercel
```

Using Netlify:

```bash
netlify deploy --prod --dir=build
```

## Structure

- `/docs` - Documentation markdown files
- `/blog` - Blog posts
- `/src` - React components and custom pages
- `/static` - Static assets like images

## Writing Documentation

1. Add markdown files to the `/docs` directory
2. Update `sidebars.js` to include new pages
3. Use frontmatter for page metadata:

```markdown
---
sidebar_position: 1
title: My Page Title
---
```

## Custom Components

Custom React components can be added to `/src/components` and imported in markdown files:

```markdown
import MyComponent from '@site/src/components/MyComponent';

<MyComponent />
```

## Configuration

Main configuration is in `docusaurus.config.js`. Update:
- Site metadata
- Navigation links
- Footer links
- Search configuration
- Theme settings

## License

Documentation is available under the same license as Docsray MCP (Apache 2.0).