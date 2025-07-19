import { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';
interface StatCardProps {
  title: string;
  value: string | ReactNode;
  description: string;
  Icon?: LucideIcon;
  iconClassName?: string;
  valueClassName?: string;
  className?: string;
}

export default function StatCard({
  title,
  value,
  description,
  Icon,
  iconClassName,
  valueClassName,
  className,
}: StatCardProps) {
  return (
    <div
      className={`bg-white p-6 rounded-lg shadow-sm border ${className}`}
    >
      {Icon && (
        <Icon
          className={`w-8 h-8 mx-auto mb-3 ${iconClassName}`}
        />
      )}
      <h3 className="font-semibold text-gray-900 mb-3">{title}</h3>
      <p className={`text-4xl font-bold ${valueClassName}`}>{value}</p>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}