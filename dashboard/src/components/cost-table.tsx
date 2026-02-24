"use client";

import { CostEntry } from "@/lib/types";
import { ENGINE_DISPLAY } from "@/lib/constants";

interface CostTableProps {
  costs: CostEntry[];
  total: number;
}

export default function CostTable({ costs, total }: CostTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 font-semibold text-gray-600">
              Provider
            </th>
            <th className="text-left py-3 px-4 font-semibold text-gray-600">
              Model
            </th>
            <th className="text-center py-3 px-4 font-semibold text-gray-600">
              Queries
            </th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600">
              Input Tokens
            </th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600">
              Output Tokens
            </th>
            <th className="text-right py-3 px-4 font-semibold text-gray-600">
              Cost
            </th>
          </tr>
        </thead>
        <tbody>
          {costs.map((c) => (
            <tr
              key={`${c.provider}-${c.model}`}
              className="border-b border-gray-100 hover:bg-gray-50"
            >
              <td className="py-3 px-4 font-medium">
                {ENGINE_DISPLAY[c.provider] || c.provider}
              </td>
              <td className="py-3 px-4 font-mono text-xs text-gray-500">
                {c.model}
              </td>
              <td className="text-center py-3 px-4">{c.queries}</td>
              <td className="text-right py-3 px-4 font-mono text-xs">
                {c.input_tokens.toLocaleString()}
              </td>
              <td className="text-right py-3 px-4 font-mono text-xs">
                {c.output_tokens.toLocaleString()}
              </td>
              <td className="text-right py-3 px-4 font-mono font-bold">
                ${c.total_cost.toFixed(4)}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-gray-300">
            <td
              colSpan={5}
              className="py-3 px-4 font-bold text-right"
            >
              Total
            </td>
            <td className="py-3 px-4 font-mono font-bold text-right text-lg">
              ${total.toFixed(4)}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
