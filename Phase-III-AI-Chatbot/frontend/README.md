# Phase III: AI Chatbot Frontend

Next.js 14 frontend with OpenAI ChatKit for conversational task management.

## Phase 1 Setup Status

✅ **Complete** - All Phase 1 frontend setup tasks finished:
- Dependencies installed (npm install)
- ChatKit provider configured in `src/context/ChatContext.tsx`
- Environment variables template created (`.env.local.example`)
- Initial chat UI shell component structure created

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS
- **AI Chat**: OpenAI ChatKit
- **State Management**: React Context (AuthContext, ChatContext)
- **API Client**: Custom fetch wrapper in `src/lib/api-client.ts`

## Project Structure

```
src/
├── app/                      # Next.js app router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Landing page
│   ├── globals.css          # Global styles
│   └── chat/
│       └── page.tsx         # Chat interface (shell in Phase 1)
├── components/
│   ├── ChatMessage.tsx      # Message display component (shell)
│   ├── ConversationList.tsx # Conversation sidebar (shell)
│   └── ToolCallBadge.tsx    # Tool execution indicator (shell)
├── context/
│   ├── AuthContext.tsx      # JWT token management (shell)
│   └── ChatContext.tsx      # ChatKit provider (configured)
├── lib/
│   └── api-client.ts        # Backend API wrapper (shell)
└── types/
    └── chat.ts              # TypeScript interfaces
```

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your settings:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### 4. Build for Production

```bash
npm run build
npm start
```

## Development Status

### Phase 1: Setup ✅ COMPLETE
- [x] Project structure created
- [x] Dependencies installed (@openai/chatkit, next, react, typescript)
- [x] Configuration files (next.config.js, tsconfig.json, tailwind.config.ts)
- [x] ChatKit provider configured
- [x] Environment variables template
- [x] Basic UI shell components
- [x] TypeScript types defined

### Phase 2: Foundational (Next)
- [ ] AuthContext implementation (T019)
- [ ] API client implementation (T021)
- [ ] TypeScript types completion (T020)

### Phase 3: User Story 1 (US1 - Task Creation)
- [ ] ChatKit integration in chat page (T035)
- [ ] API chat route proxy (T036)
- [ ] ChatMessage component implementation (T037)
- [ ] ToolCallBadge component implementation (T038)
- [ ] Auth + ChatKit integration (T039)
- [ ] Error handling UI (T040)

### Phase 4: User Story 2 (US2 - View Tasks)
- [ ] Task list rendering in ChatMessage (T049-T050)

### Phase 8: User Story 6 (US6 - Resume Conversations)
- [ ] ConversationList implementation (T082-T086)

## Component Status

| Component | Phase 1 Status | Implementation Phase |
|-----------|---------------|---------------------|
| ChatContext.tsx | ✅ Configured | Phase 1 (Complete) |
| AuthContext.tsx | 🔨 Shell | Phase 2 (T019) |
| ChatMessage.tsx | 🔨 Shell | Phase 3 (T037) |
| ConversationList.tsx | 🔨 Shell | Phase 8 (T082-T086) |
| ToolCallBadge.tsx | 🔨 Shell | Phase 3 (T038) |
| api-client.ts | 🔨 Shell | Phase 2 (T021) |
| chat.ts (types) | ✅ Defined | Phase 1 (Complete) |

Legend:
- ✅ Complete and functional
- 🔨 Shell structure (interface defined, implementation pending)

## Testing

```bash
# Run unit tests (when implemented in Phase 3+)
npm test

# Run E2E tests (when implemented in Phase 3+)
npm run test:e2e
```

## Deployment

Deploy to Vercel:

```bash
vercel deploy
```

Environment variables required in Vercel:
- `NEXT_PUBLIC_BACKEND_URL` - Backend API URL (Railway deployment)

## Next Steps

1. **Phase 2**: Implement foundational components (AuthContext, API client)
2. **Phase 3**: Integrate ChatKit for message sending and display
3. **Phase 8**: Add conversation persistence and sidebar

## Notes

- All shell components have clear TODO comments indicating which phase/task implements them
- TypeScript interfaces are fully defined in Phase 1 for type safety during development
- ChatKit is configured but not yet integrated into the chat UI (Phase 3)
- Backend API client is stubbed with correct method signatures for API contracts
