# Academic LLM Frontend

Next.js frontend for the Academic LLM Fine-Tuning System.

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
npm install
```

2. **Set up environment variables:**
```bash
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL to your backend URL
```

3. **Run development server:**
```bash
npm run dev
```

4. **Open in browser:**
```
http://localhost:3000
```

## 📦 Build for Production

```bash
npm run build
npm start
```

## 🌐 Deploy to Vercel

See [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md) for detailed deployment instructions.

## 🔧 Configuration

### Environment Variables

- `NEXT_PUBLIC_API_URL`: Backend API URL (required)
  - Local: `http://localhost:8000`
  - Production: Your GPU server URL (e.g., `https://api.yourdomain.com`)

### API Endpoints

The frontend calls these backend endpoints:
- `GET /health` - Health check
- `POST /search` - RAG search
- `POST /chat` - Chat with model
- `POST /compare` - Compare models

## 📁 Project Structure

```
frontend/
├── app/              # Next.js app directory
│   ├── layout.tsx    # Root layout
│   ├── page.tsx      # Home page
│   └── globals.css   # Global styles
├── components/       # React components
│   ├── ChatInterface.tsx
│   ├── SearchInterface.tsx
│   └── StatusCard.tsx
├── lib/              # Utilities
│   └── api.ts        # API client
└── public/           # Static assets
```

## 🛠️ Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **Lucide React** - Icons

