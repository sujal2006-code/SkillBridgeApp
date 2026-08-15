import React from 'react';

interface CircularProgressProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  bgColor?: string;
  textColor?: string;
  fontSize?: string;
  label?: string;
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  percentage,
  size = 64,
  strokeWidth = 4,
  color = '#00687a',
  bgColor = '#e0e3e5',
  textColor = '#191c1e',
  fontSize = 'text-sm font-semibold',
  label
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center justify-center shrink-0" style={{ width: size, height: size }}>
      <svg className="w-full h-full transform -rotate-90" viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={bgColor}
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`${fontSize} font-['Hanken_Grotesk']`} style={{ color: textColor }}>
          {percentage}%
        </span>
        {label && <span className="text-[10px] text-gray-500">{label}</span>}
      </div>
    </div>
  );
};
