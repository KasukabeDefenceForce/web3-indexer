import  {
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"
import type { ColumnDef } from "@tanstack/react-table"
import { useQuery } from "@tanstack/react-query"
import axios from "axios"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table"

export type Transfer = {
  from: string
  to: string
  amount: number
  blockNumber: number
}

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
}

export const columns: ColumnDef<Transfer>[] = [
  {
    accessorKey: "blockNumber",
    header: "Block",
  },
  {
    accessorKey: "from",
    header: "From Address",
  },
  {
    accessorKey: "to",
    header: "To Address",
  },
  {
    accessorKey: "amount",
    header: "Amount (USDC)",
  },
]

function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
  })

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                )
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  )
}

export function TransfersTable() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['transfers'],
    queryFn: async () => {
      const response = await axios.get('http://127.0.0.1:5000/transfers');
      return response.data.data as Transfer[];
    },
    refetchInterval: 3000, 
  });

  if (isLoading) {
    return <div>Loading transfers...</div>
  }

  if (isError) {
    return <div>Error fetching data. Please try again later.</div>
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Recent Transfers</h1>
      <DataTable columns={columns} data={data || []} />
    </div>
  )
}