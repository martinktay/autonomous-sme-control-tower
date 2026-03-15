"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Upload as UploadIcon,
  FileText,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { uploadInvoice } from "@/lib/api";
import { useOrg } from "@/lib/org-context";
import Link from "next/link";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const { orgId } = useOrg();
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
  const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];

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
      if (!ALLOWED_TYPES.includes(selected.type) && !selected.name.match(/\.(pdf|jpe?g|png)$/i)) {
        setError('Unsupported file type. Please upload a PDF, JPG, or PNG file.');
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
      const data = await uploadInvoice(orgId, file);
      setResult(data);
      setFile(null);
    } catch (err: any) {
      setError(err.message || "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Upload Invoice</h1>
        <p className="text-muted-foreground">
          Upload a PDF or image of your invoice. The AI will read it and add
          the information to your business data automatically.
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Select Your Invoice</CardTitle>
          <CardDescription>
            Accepted formats: PDF, JPG, PNG. Maximum one file at a time.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Drop zone */}
          <label
            htmlFor="file-upload"
            className="block border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-primary/50 hover:bg-accent/30 transition-colors"
          >
            {file ? (
              <div className="flex items-center justify-center gap-3">
                <FileText className="h-8 w-8 text-primary" />
                <div className="text-left">
                  <p className="font-medium">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024).toFixed(0)} KB — Ready to upload
                  </p>
                </div>
              </div>
            ) : (
              <div>
                <UploadIcon className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
                <p className="font-medium mb-1">
                  Click here to select your invoice
                </p>
                <p className="text-sm text-muted-foreground">
                  or drag and drop a file
                </p>
              </div>
            )}
            <input
              type="file"
              accept=".pdf,image/*"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
          </label>

          {/* Upload button */}
          <Button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full gap-2"
            size="lg"
          >
            {uploading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Processing your invoice...
              </>
            ) : (
              <>
                <UploadIcon className="h-4 w-4" />
                Upload Invoice
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Error message */}
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

      {/* Success result */}
      {result && (
        <Card className="border-green-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
              Invoice Uploaded Successfully
            </CardTitle>
            <CardDescription>
              The AI has processed your invoice. Here is what was extracted:
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="rounded-lg bg-muted p-4 space-y-2">
              {result.signal_id && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Reference ID</span>
                  <Badge variant="outline">{result.signal_id}</Badge>
                </div>
              )}
              {result.extracted_data?.vendor_name && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Vendor</span>
                  <span className="font-medium">
                    {result.extracted_data.vendor_name}
                  </span>
                </div>
              )}
              {result.extracted_data?.amount && (
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Amount</span>
                  <span className="font-medium">
                    {result.extracted_data.amount}
                  </span>
                </div>
              )}
            </div>

            <div className="flex gap-2 pt-2">
              <Link href="/dashboard" className="flex-1">
                <Button variant="outline" className="w-full">
                  View Dashboard
                </Button>
              </Link>
              <Link href="/portal" className="flex-1">
                <Button className="w-full">Run Analysis</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Helpful tip */}
      <Card className="mt-6">
        <CardContent className="py-4">
          <p className="text-sm text-muted-foreground">
            <span className="font-medium text-foreground">Tip:</span> After
            uploading, go to{" "}
            <Link href="/portal" className="text-primary underline">
              Run Analysis
            </Link>{" "}
            to see how this invoice affects your business health score.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
