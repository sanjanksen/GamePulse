// @ts-ignore
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
// @ts-ignore
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm";

// Read environment variables (do NOT hardcode secrets!)

// @ts-ignore
const SUPABASE_URL = Deno.env.get("MY_SUPABASE_URL")!;
// @ts-ignore
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("MY_SUPABASE_SERVICE_ROLE_KEY")!;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

serve(async (req: Request) => {
  try {
    const { gameCode } = await req.json().catch(() => ({}));
    if (!gameCode) {
      return new Response(JSON.stringify({ error: "Missing gameCode" }), { status: 400, headers: { "Content-Type": "application/json" } });
    }

    const now = new Date().toISOString();

    const { data, error } = await supabase
      .from("lobbies")
      .update({ beginning_time: now })
      .eq("code", gameCode)
      .select();

    if (error) return new Response(JSON.stringify({ error: error.message }), { status: 500, headers: { "Content-Type": "application/json" } });
    if (!data || data.length === 0) return new Response(JSON.stringify({ error: "Game code not found" }), { status: 404, headers: { "Content-Type": "application/json" } });

    return new Response(JSON.stringify({ message: "Lobby updated", lobby: data[0] }), { status: 200, headers: { "Content-Type": "application/json" } });

  } catch (err) {
    // @ts-ignore
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers: { "Content-Type": "application/json" } });
  }
});
