import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen } from 'lucide-react';

interface BookItem {
  id: string;
  color: string;
  title: string;
  position: number;
}

interface AnimatedLibraryProps {
  books: BookItem[];
  isSyncing: boolean;
  onBookClick: (folderName: string) => void;
}

export function AnimatedLibrary({ books, isSyncing, onBookClick }: AnimatedLibraryProps) {
  const [hoveredBook, setHoveredBook] = useState<BookItem | null>(null);

  // Group books into shelves (max 10 per shelf)
  const shelves = [];
  for (let i = 0; i < Math.max(books.length, 10); i += 10) {
    shelves.push(books.slice(i, i + 10));
  }

  return (
    <div className="relative w-full h-full flex flex-col justify-end gap-6 px-4 py-8 bg-surface-container-lowest/50 rounded-2xl backdrop-blur-md border border-white/20 shadow-inner">
      
      {/* Tooltip (Glassmorphism) */}
      <AnimatePresence>
        {hoveredBook && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="absolute top-4 left-1/2 -translate-x-1/2 bg-white/40 backdrop-blur-xl border border-white/60 p-4 rounded-xl shadow-xl z-30 min-w-[200px]"
          >
            <h3 className="text-sm font-bold text-neutral-800 break-words mb-1">
              {hoveredBook.title}
            </h3>
            <p className="text-xs text-neutral-600 flex items-center gap-1">
              <BookOpen size={12} /> Cliquer pour ouvrir
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Shelves */}
      {shelves.map((shelfBooks, shelfIdx) => (
        <div key={shelfIdx} className="relative w-full h-24 flex items-end justify-start px-4 gap-2">
          {/* Shelf Base */}
          <div className="absolute bottom-0 left-0 right-0 h-3 bg-gradient-to-b from-neutral-200 to-neutral-300 rounded-sm shadow-md" />
          
          {/* Books */}
          <AnimatePresence>
            {shelfBooks.map((book) => (
              <motion.div
                key={book.id}
                layoutId={`book-${book.id}`}
                initial={{ opacity: 0, y: -20, rotate: -10 }}
                animate={{ opacity: 1, y: 0, rotate: 0 }}
                whileHover={{ y: -10, scale: 1.05 }}
                onMouseEnter={() => setHoveredBook(book)}
                onMouseLeave={() => setHoveredBook(null)}
                onClick={() => onBookClick(book.id)}
                className="relative cursor-pointer z-10"
                style={{
                  width: '24px',
                  height: `${60 + (book.position % 5) * 5}px`,
                  backgroundColor: book.color,
                  borderRadius: '3px 4px 4px 3px',
                  boxShadow: 'inset -2px 0 5px rgba(0,0,0,0.2), 2px 2px 5px rgba(0,0,0,0.1)'
                }}
              >
                {/* Book spine details */}
                <div className="absolute left-1 top-2 bottom-2 w-1 bg-white/20 rounded-full" />
                <div className="absolute right-1 top-2 bottom-2 w-0.5 bg-black/10" />
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Syncing animation (Robot putting a new book) */}
          <AnimatePresence>
            {isSyncing && shelfIdx === shelves.length - 1 && (
              <motion.div
                initial={{ opacity: 0, x: -50, y: -50 }}
                animate={{ opacity: 1, x: 0, y: 0 }}
                exit={{ opacity: 0 }}
                className="relative z-20 opacity-50"
                style={{ width: '24px', height: '70px', backgroundColor: '#9CA3AF', borderRadius: '3px 4px 4px 3px' }}
              >
                <div className="absolute -top-6 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-blue-500 animate-ping" />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      ))}
    </div>
  );
}
