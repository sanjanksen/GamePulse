// @ts-ignore
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
// @ts-ignore
import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm";

// Environment variables
// @ts-ignore
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
// @ts-ignore
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

serve(async (req: Request) => {
  try {
    // Parse JSON body
    const { gameCode, isFinished } = await req.json().catch(() => ({}));
    if (!gameCode) {
      return new Response(JSON.stringify({ error: "Missing gameCode" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (typeof isFinished !== "boolean") {
      return new Response(JSON.stringify({ error: "Missing or invalid isFinished value" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Fetch the lobby row
    const { data: lobbies, error: fetchError } = await supabase
      .from("lobbies")
      .select("*")
      .eq("code", gameCode);

    if (fetchError) {
      return new Response(JSON.stringify({ error: fetchError.message }), { 
        status: 500, 
        headers: { "Content-Type": "application/json" } 
      });
    }

    if (!lobbies || lobbies.length === 0) {
      return new Response(JSON.stringify({ error: "Game code not found" }), { 
        status: 404, 
        headers: { "Content-Type": "application/json" } 
      });
    }

    // Update is_finished to the value from the request
    const { data, error } = await supabase
      .from("lobbies")
      .update({ is_finished: isFinished })
      .eq("code", gameCode)
      .select();

    if (error) {
      return new Response(JSON.stringify({ error: error.message }), { 
        status: 500, 
        headers: { "Content-Type": "application/json" } 
      });
    }

    return new Response(JSON.stringify({ message: "Game updated", lobby: data[0] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });

  } catch (err) {
    // @ts-ignore
    return new Response(JSON.stringify({ error: err.message }), { 
      status: 500, 
      headers: { "Content-Type": "application/json" } 
    });
  }
});
