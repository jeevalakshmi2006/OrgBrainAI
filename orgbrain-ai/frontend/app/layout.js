import "./globals.css";

export const metadata = {
  title: "OrgBrain AI",
  description: "Organizational Knowledge Preservation & Department AI Twin Platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
