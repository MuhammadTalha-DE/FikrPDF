#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/../frontend/src/app"

declare -A PAGES=(
  ["split"]="Split PDF|Extract pages or split into parts."
  ["compress"]="Compress PDF|Shrink file size without losing quality."
  ["rotate"]="Rotate PDF|Rotate pages and reorder them."
  ["image-to-pdf"]="Image → PDF|JPG, PNG, WebP to PDF in one click."
  ["pdf-to-image"]="PDF → Image|Convert pages to JPG or PNG."
  ["pdf-to-word"]="PDF → Word|Editable Word docs from any PDF."
  ["word-to-pdf"]="Word → PDF|Convert DOCX to polished PDF."
  ["pdf-to-excel"]="PDF → Excel|Extract tables to spreadsheets."
  ["protect"]="Protect PDF|Add password and permissions."
  ["unlock"]="Unlock PDF|Remove password you already know."
  ["watermark"]="Watermark PDF|Stamp text or image watermark."
  ["sign"]="Sign PDF|Draw or upload a signature."
  ["page-numbers"]="Page Numbers|Add headers and page numbers."
  ["ocr"]="OCR PDF|Make scanned PDFs searchable."
  ["chat"]="Chat with PDF|Ask questions, get answers."
  ["summarize"]="Summarize PDF|Key points in seconds."
  ["translate"]="Translate PDF|Convert to any language."
)

for slug in "${!PAGES[@]}"; do
  IFS="|" read -r title desc <<< "${PAGES[$slug]}"
  mkdir -p "$slug"
  cat > "$slug/page.tsx" <<EOF
import { Container } from "@/components/ui/Container";
import { Card, CardBody } from "@/components/ui/Card";

export default function Page() {
  return (
    <Container className="py-16">
      <h1 className="font-display text-3xl font-bold">${title}</h1>
      <p className="mt-2 text-ink-600">${desc}</p>
      <Card className="mt-8">
        <CardBody className="text-sm text-ink-500">
          Implementation arrives in a later phase.
        </CardBody>
      </Card>
    </Container>
  );
}
EOF
done

echo "Created placeholder pages."