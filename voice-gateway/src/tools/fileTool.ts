export type FileOperationArgs = {
  operation: 'create' | 'read' | 'write' | 'append' | 'insert' | 'replace' | 'save_as';
  filename?: string;
  content?: string;
  line_number?: number;
  pattern?: string;
  replacement?: string;
};
export async function fileOperationTool(args: FileOperationArgs) {
  const res = await fetch('http://localhost:8000/tools/file_operation', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(args)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`file_operation failed: ${res.status} ${JSON.stringify(err)}`);
  }
  return await res.json();
}


