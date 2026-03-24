/**
 * @file Finance Upload page (/finance/upload) — Upload financial documents and spreadsheets.
 * Supports PDF, images, CSV, and Excel with AI extraction and anomaly detection.
 */
"use client";

import { useState } from "react";
import {
  Card, CardContent, CardDescription, CardHeader, CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Upload as UploadIcon, FileText, CheckCircle2, AlertCircle, Loader2,
} from "lucide-react";
import { uploadFinanceDocument } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import Link from "next/link";

export default function FinanceUploadPage() {
  const { orgId } = useOrg();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
  const ALLOWED_TYPES = [
    'application/pdf', 'image/jpeg', 'image/png', 'image/jpg',
    'text/csv', 'application/csv', 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  ];

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] || null;
    setError(null);
    if (selected) {
      if (selected.size > MAX_FILE_SIZE) {
        setError(`File is too large (${(selected.size / 1024 / 1024).toFixed(1)} MB). Maximum is 10 MB.`);
        setFile(null);
        return;
      }
      if (selected.size === 0) {
        setError('File is empty. Please select a valid file.');
        setFile(null);
        return;
      }
      if (!ALLOWED_TYPES.includes(selected.type) && !selected.name.match(/\.(pdf|jpe?g|png|csv|xlsx?|xls)$/i)) {
        setError('Unsupported file type. Accepted: PDF, JPEG, PNG, CSV, XLS, XLSX.');
        setFile(null);
        return;
      }
    }
    setFile(selected);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      const data = await uploadFinanceDocument(orgId, file);
      setResult(data);
      setFile(null);
    } catch (err: any) {
      setError(err.message || "Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const ext = result?.extracted_data;

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Upload Financial Document</h1>
        <p className="text-muted-foreground">
          Upload a PDF, image, or spreadsheet (CSV/Excel) of your invoices, receipts, or financial records.
          The AI will extract key fields and classify them automatically.
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Select Document</CardTitle>
          <CardDescription>Accepted: PDF, JPEG, PNG, CSV, XLS, XLSX (max 10 MB)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <label
            htmlFor="finance-file"
            className="block border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-accent/30 transition-colors"
          >
            {file ? (
              <div className="flex items-center justify-center gap-3">
                <FileText className="h-8 w-8 text-primary" />
                <div className="text-left">
                  <p className="font-medium">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024).toFixed(0)} KB
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <UploadIcon className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
                <p className="font-medium mb-1">Click to select a file</p>
                <p className="text-sm text-muted-foreground">or drag and drop</p>
              </div>
            )}
            <input
              type="file"
              accept=".pdf,image/jpeg,image/png,.csv,.xls,.xlsx"
              onChange={handleFileSelect}
              className="hidden"
              id="finance-file"
            />
          </label>

          <Button onClick={handleUpload} disabled={!file || uploading} className="w-full gap-2" size="lg">
            {uploading ? (
              <><Loader2 className="h-4 w-4 animate-spin" />Processing...</>
            ) : (
              <><UploadIcon className="h-4 w-4" />Upload Document</>
            )}
          </Button>
        </CardContent>
      </Card>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="py-4">
            <div className="flex items-center gap-2 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <p className="text-sm">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {result && (
        <Card className="border-green-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              {result.records_imported != null ? "Spreadsheet Imported" : "Document Processed"}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Spreadsheet import result */}
            {result.records_imported != null && (
              <div className="rounded-lg bg-muted p-4 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Source File</span>
                  <span className="font-medium">{result.source_file}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Records Imported</span>
                  <span className="font-medium">{result.records_imported}</span>
                </div>
                {result.records?.slice(0, 5).map((r: any, i: number) => (
                  <div key={i} className="flex justify-between text-xs text-muted-foreground border-t pt-1">
                    <span>{r.vendor}</span>
                    <span>{r.amount}</span>
                  </div>
                ))}
                {result.records_imported > 5 && (
                  <p className="text-xs text-muted-foreground">...and {result.records_imported - 5} more</p>
                )}
              </div>
            )}

            {/* Single document result */}
            {ext && (
              <div className="rounded-lg bg-muted p-4 space-y-2 text-sm">
                {ext?.vendor_name && (
                  <div className="flex justify-between"><span className="text-muted-foreground">Vendor</span><span className="font-medium">{ext.vendor_name}</span></div>
                )}
                {ext?.amount != null && (
                  <div className="flex justify-between"><span className="text-muted-foreground">Amount</span><span className="font-medium">{ext.currency} {ext.amount}</span></div>
                )}
                {ext?.category && (
                  <div className="flex justify-between"><span className="text-muted-foreground">Category</span><Badge variant="outline">{ext.category}</Badge></div>
                )}
                {ext?.confidence_score != null && (
                  <div className="flex justify-between"><span className="text-muted-foreground">Confidence</span><span>{(ext.confidence_score * 100).toFixed(0)}%</span></div>
                )}
                {ext?.flags?.length > 0 && (
                  <div className="pt-2 space-y-1">
                    {ext.flags.map((f: any, i: number) => (
                      <Badge key={i} variant="destructive" className="mr-1">{f.flag_type}: {f.flag_reason}</Badge>
                    ))}
                  </div>
                )}
              </div>
            )}

            {result.status === "needs_review" && (
              <p className="text-sm text-amber-600">This document was sent to the review queue.</p>
            )}

            <div className="flex gap-2 pt-2">
              <Link href="/finance" className="flex-1">
                <Button variant="outline" className="w-full">Finance Dashboard</Button>
              </Link>
              <Link href="/finance/review" className="flex-1">
                <Button className="w-full">Review Queue</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
