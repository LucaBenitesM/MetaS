import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {
  title: "Meta Ads AI · Espacio de trabajo",
  description:
    "Planificación y optimización supervisada de campañas. Demo independiente, sin conexión a Meta.",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
