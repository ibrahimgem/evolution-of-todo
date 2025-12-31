'use client';

import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const Card: React.FC<CardProps> & {
  Header: React.FC<CardHeaderProps>;
  Body: React.FC<CardBodyProps>;
  Footer: React.FC<CardFooterProps>;
} = ({ children, className = '', hover = false, padding = 'md' }) => {
  const paddingClasses = {
    none: '',
    sm: 'p-3',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div
      className={`
        bg-white/90 backdrop-blur-xl
        rounded-2xl shadow-xl shadow-gray-200/50
        border border-white/20
        transition-all duration-300 ease-out
        ${hover ? 'cursor-pointer hover:shadow-2xl hover:shadow-gray-300/50 hover:-translate-y-1' : ''}
        ${paddingClasses[padding]}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  description?: string;
}

const CardHeader: React.FC<CardHeaderProps> = ({ children, className = '', title, description }) => {
  return (
    <div className={`px-6 pb-4 border-b border-gray-100 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 tracking-tight">
          {title}
        </h3>
      )}
      {description && (
        <p className="mt-1 text-sm text-gray-500">
          {description}
        </p>
      )}
      {children}
    </div>
  );
};

interface CardBodyProps {
  children: React.ReactNode;
  className?: string;
}

const CardBody: React.FC<CardBodyProps> = ({ children, className = '' }) => {
  return (
    <div className={`${className}`}>
      {children}
    </div>
  );
};

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
  dividers?: boolean;
}

const CardFooter: React.FC<CardFooterProps> = ({ children, className = '', dividers = false }) => {
  return (
    <div className={`
      px-6 py-4 bg-gray-50/50 rounded-b-2xl
      ${dividers ? 'border-t border-gray-100' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
};

Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

export default Card;
