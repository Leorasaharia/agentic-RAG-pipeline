import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.auth.router import router as auth_router
from backend.documents.router import router as docs_router
from backend.agents.orchestrator import RAGOrchestrator
from backend.db.session import engine, Base
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Scalable Multi-Agent RAG Platform")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Sub-routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(docs_router, prefix="/api", tags=["documents"])

orchestrator = RAGOrchestrator()

@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket, token: str = None):
    """
    WebSocket streaming endpoint.
    Expects auth via query param token = 'Bearer ...' for simplicity in WebSockets.
    """
    await websocket.accept()

    # We skip strict dependency injection for JWT parsing in this basic mock version,
    # but normally we'd decode token here.
    if not token:
        await websocket.send_text("Error: Missing authentication token")
        await websocket.close()
        return

    logger.info("WebSocket Client Connected to /ws/chat")
    try:
        while True:
            # 1. Receiver explicit query from Client
            query = await websocket.receive_text()
            logger.info(f"Received query: {query}")

            try:
                # 2. Start RAG Orchestra Generator
                response_stream = orchestrator.process_query_stream(query)

                # 3. Stream tokens asynchronously back to client
                for token_chunk in response_stream:
                    # To prevent blocking the main asyncio event loop completely, we do light sleep.
                    # RAG model yielding is blocking if not run in a threadpool, 
                    # but the generator inherently releases some control.
                    await asyncio.sleep(0.01)
                    await websocket.send_text(token_chunk)

            except Exception as stream_err:
                logger.error(f"Error during streaming: {stream_err}")
                await websocket.send_text("[Stream Error Encountered]")
                await websocket.send_text("[DONE]")

    except WebSocketDisconnect:
        logger.info("WebSocket Client disconnected")
    except Exception as e:
        logger.error(f"Unexpected WS Error: {e}")
        await websocket.close()


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
