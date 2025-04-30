import Image from "next/image";
import { Geist, Geist_Mono } from "next/font/google";
import { FileUploader } from "@/components/FileUploader";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function Home() {
  return (
    <div>
      <h1 className="text-3xl text-center font-bold mt-6">PIXEL PEEP CHALLENGE</h1>
      <FileUploader></FileUploader>
    </div>
  );
}
