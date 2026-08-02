"use client";
import { useEffect, useRef } from "react";

/**
 * Animated force-directed graph, drawn on canvas, no external graph library.
 * Nodes = departments (radius scales with how much SOP knowledge is collected).
 * Edges = department relatedness (thickness scales with shared skills).
 * A light physics simulation (repulsion + spring + gentle jitter) keeps it alive.
 */
export default function KnowledgeGraph({ nodes, edges, width = 640, height = 420 }) {
  const canvasRef = useRef(null);
  const stateRef = useRef({ nodes: [], edges: [] });
  const animRef = useRef(null);

  useEffect(() => {
    if (!nodes || nodes.length === 0) return;

    const cx = width / 2;
    const cy = height / 2;
    const simNodes = nodes.map((n, i) => {
      const angle = (i / nodes.length) * Math.PI * 2;
      return {
        ...n,
        x: cx + Math.cos(angle) * 120,
        y: cy + Math.sin(angle) * 120,
        vx: 0,
        vy: 0,
        radius: 28 + Math.min(n.knowledge_count, 8) * 6,
      };
    });
    const simEdges = edges.map((e) => ({ ...e }));
    stateRef.current = { nodes: simNodes, edges: simEdges };

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.scale(dpr, dpr);

    const NAVY = "#0f2942";
    const STEEL = "#3b6ea5";

    function tick() {
      const { nodes: ns, edges: es } = stateRef.current;

      // Repulsion between all node pairs
      for (let i = 0; i < ns.length; i++) {
        for (let j = i + 1; j < ns.length; j++) {
          const a = ns[i], b = ns[j];
          const dx = b.x - a.x, dy = b.y - a.y;
          const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
          const minDist = a.radius + b.radius + 40;
          const force = dist < minDist ? (minDist - dist) * 0.02 : -800 / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          a.vx -= fx; a.vy -= fy;
          b.vx += fx; b.vy += fy;
        }
      }

      // Spring attraction along edges
      es.forEach((e) => {
        const a = ns.find((n) => n.id === e.source);
        const b = ns.find((n) => n.id === e.target);
        if (!a || !b) return;
        const dx = b.x - a.x, dy = b.y - a.y;
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
        const targetDist = 180 - Math.min(e.weight, 5) * 15;
        const force = (dist - targetDist) * 0.01;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        a.vx += fx; a.vy += fy;
        b.vx -= fx; b.vy -= fy;
      });

      // Gentle pull to center + tiny random jitter (keeps it visibly "alive")
      ns.forEach((n) => {
        n.vx += (cx - n.x) * 0.002;
        n.vy += (cy - n.y) * 0.002;
        n.vx += (Math.random() - 0.5) * 0.15;
        n.vy += (Math.random() - 0.5) * 0.15;
        n.vx *= 0.9;
        n.vy *= 0.9;
        n.x += n.vx;
        n.y += n.vy;
        n.x = Math.max(n.radius, Math.min(width - n.radius, n.x));
        n.y = Math.max(n.radius, Math.min(height - n.radius, n.y));
      });

      // Draw
      ctx.clearRect(0, 0, width, height);

      es.forEach((e) => {
        const a = ns.find((n) => n.id === e.source);
        const b = ns.find((n) => n.id === e.target);
        if (!a || !b) return;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.strokeStyle = `rgba(59, 110, 165, ${0.25 + Math.min(e.weight, 5) * 0.1})`;
        ctx.lineWidth = 1 + Math.min(e.weight, 5);
        ctx.stroke();
      });

      ns.forEach((n) => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        const gradient = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.radius);
        gradient.addColorStop(0, STEEL);
        gradient.addColorStop(1, NAVY);
        ctx.fillStyle = gradient;
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = "#ffffff";
        ctx.stroke();

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 12px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        wrapText(ctx, n.name, n.x, n.y - 4, n.radius * 1.7, 13);

        ctx.font = "10px sans-serif";
        ctx.fillStyle = "rgba(255,255,255,0.85)";
        ctx.fillText(`${n.knowledge_count} SOPs`, n.x, n.y + n.radius - 12);
      });

      animRef.current = requestAnimationFrame(tick);
    }

    function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
      const words = text.split(" ");
      let line = "";
      const lines = [];
      for (const w of words) {
        const test = line + w + " ";
        if (ctx.measureText(test).width > maxWidth && line) {
          lines.push(line);
          line = w + " ";
        } else {
          line = test;
        }
      }
      lines.push(line);
      const startY = y - ((lines.length - 1) * lineHeight) / 2;
      lines.forEach((l, i) => ctx.fillText(l.trim(), x, startY + i * lineHeight));
    }

    tick();
    return () => cancelAnimationFrame(animRef.current);
  }, [nodes, edges, width, height]);

  if (!nodes || nodes.length === 0) {
    return <p className="text-gray-400 text-sm py-12 text-center">No department knowledge yet.</p>;
  }

  return <canvas ref={canvasRef} className="w-full" />;
}
