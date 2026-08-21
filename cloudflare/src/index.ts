/**
 * Nanobot Cloudflare Computer Runtime Adapter
 * Powered by @cloudflare/computer and Cloudflare Durable Objects.
 */

export interface Env {
  COMPUTER_FS: DurableObjectNamespace;
  TELEGRAM_BOT_TOKEN?: string;
  NOTION_TOKEN?: string;
  MISTRAL_API_KEY?: string;
}

export class NanobotComputerDO {
  state: DurableObjectState;
  storage: DurableObjectStorage;

  constructor(state: DurableObjectState, env: Env) {
    this.state = state;
    this.storage = state.storage;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    
    // Virtual Filesystem & Tool Execution
    if (url.pathname === "/exec") {
      const { command } = await request.json() as { command: string };
      // Worker Shell (just-bash) simulation in V8 Isolate (<5ms)
      return Response.json({
        status: "success",
        runtime: "cloudflare_v8_isolate",
        command: command,
        output: `Executed: ${command} on Durable Object filesystem`
      });
    }
    
    return Response.json({ status: "active", engine: "@cloudflare/computer" });
  }
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    // Health check endpoint
    if (url.pathname === "/health" || url.pathname === "/") {
      return Response.json({
        app: "Nanobot 🐈",
        runtime: "Cloudflare Computer / Edge Workers",
        status: "healthy",
        edge_region: request.cf?.colo || "global"
      });
    }

    // Telegram Webhook Handler
    if (url.pathname === "/telegram/webhook" && request.method === "POST") {
      try {
        const update = await request.json() as any;
        const message = update.message || update.edited_message;
        
        if (!message || !message.text) {
          return new Response("OK");
        }

        const text = message.text.trim();
        const chatId = message.chat.id;
        const userId = message.from?.id;

        // Security check
        if (userId !== 1449852069) {
          return new Response("Unauthorized", { status: 403 });
        }

        // Fast-path routing on Cloudflare Edge
        let responseText = "🐈 Nanobot sẵn sàng hỗ trợ.";
        if (text.toLowerCase().includes("cân") || text.toLowerCase().includes("ms4980")) {
          responseText = "📋 [Cloudflare Edge Fact]: 15 Cân Charder MS4980 phân bổ tại các khoa phòng. Trệt A (T24002396), Da Liễu (T24002392), Ung Bướu 1D (T24002393).";
        } else if (text.toLowerCase().includes("spo2") || text.toLowerCase().includes("rad-5v")) {
          responseText = "🩺 [Cloudflare Edge Fact]: 10 Máy SpO2 Rad-5v (3 Cấp Cứu, 7 Khám Bệnh/P.2009 Chuẩn bị).";
        }

        return Response.json({
          method: "sendMessage",
          chat_id: chatId,
          text: responseText
        });
      } catch (err: any) {
        return Response.json({ error: err.message }, { status: 500 });
      }
    }

    return new Response("Not Found", { status: 404 });
  }
};
