import type { Metadata } from "next";
import Script from "next/script";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Drafter Analiser",
  description: "Word Add-in untuk analisis draft peraturan",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <head>
        {/*
          Office.js melumpuhkan history.pushState dan history.replaceState —
          itu caranya mencegah add-in berpindah halaman keluar dari task pane.
          Router Next.js dan overlay dev-nya membutuhkan keduanya, sehingga
          tanpa penjaga ini halaman gagal dirender dengan error
          "window.history.replaceState is not a function".

          Skrip ini menyimpan fungsi aslinya SEBELUM office.js dimuat, lalu
          mengembalikannya bila dihapus. office.js memuat berkas lanjutan
          secara asinkron, jadi pemulihannya diulang beberapa detik, bukan
          sekali jalan. Urutan penulisan di sini menentukan urutan pemuatan —
          jangan ditukar dengan tag office.js di bawahnya.
        */}
        <Script id="jaga-history-api" strategy="beforeInteractive">
          {`(function () {
  var h = window.history;
  var asli = {
    pushState: typeof h.pushState === 'function' ? h.pushState.bind(h) : null,
    replaceState: typeof h.replaceState === 'function' ? h.replaceState.bind(h) : null
  };
  function pulihkan() {
    ['pushState', 'replaceState'].forEach(function (nama) {
      if (typeof h[nama] !== 'function' && asli[nama]) {
        try { h[nama] = asli[nama]; } catch (e) {}
      }
    });
  }
  var sisa = 40;
  var timer = setInterval(function () {
    pulihkan();
    if (--sisa <= 0) clearInterval(timer);
  }, 100);
  window.addEventListener('load', pulihkan);
})();`}
        </Script>
        <Script
          src="https://appsforoffice.microsoft.com/lib/1/hosted/office.js"
          strategy="beforeInteractive"
        />
      </head>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
