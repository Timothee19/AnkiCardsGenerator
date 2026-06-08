import { motion, AnimatePresence } from 'motion/react';
import { BookOpen, RefreshCw } from 'lucide-react';

interface Book {
  id: string;
  color: string;
  title: string;
  position: number; // 0 to 14
}

interface LibraryShelfProps {
  books: Book[];
  isSyncing: boolean;
}

export const LibraryShelf = ({ books, isSyncing }: LibraryShelfProps) => {
  return (
    <div className="bg-surface rounded-2xl border border-outline-variant flex flex-col h-full overflow-hidden shadow-sm w-full max-w-sm mx-auto">
      <div className="border-l-4 border-primary p-4 bg-surface-container-lowest border-b border-outline-variant flex justify-between items-center">
        <h2 className="text-lg font-bold text-on-surface flex items-center gap-2">
          <BookOpen className="text-primary" size={20} />
          Library
        </h2>
        {isSyncing && (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <RefreshCw size={14} className="text-on-surface-variant" />
          </motion.div>
        )}
      </div>
      
      <div className="p-6 flex-grow flex flex-col items-center justify-center relative bg-surface-container-low/20 min-h-[300px]">
        {/* Modern Empty Shelves */}
        <div className="w-full h-full border-2 border-outline-variant/20 rounded-xl bg-surface-container-lowest/50 relative p-4 flex flex-col justify-between min-h-[220px]">
          {[0, 1, 2].map((shelfIdx) => (
            <div key={shelfIdx} className="h-[60px] border-b-2 border-outline-variant/30 relative flex items-end gap-2 px-2">
              <AnimatePresence>
                {books
                  .filter(b => Math.floor(b.position / 5) === shelfIdx)
                  .map((book) => (
                    <motion.div
                      key={book.id}
                      initial={{ opacity: 0, scale: 0.8, y: -20 }}
                      animate={{ opacity: 1, scale: 1, y: 0 }}
                      className="w-5 h-[45px] rounded-sm shadow-md cursor-pointer group relative"
                      style={{ backgroundColor: book.color }}
                      whileHover={{ y: -5, scale: 1.1 }}
                    >
                      <div className="absolute inset-x-0 top-1 h-0.5 bg-white/20" />
                      <div className="absolute inset-x-0 bottom-2 h-1 bg-black/10" />
                    </motion.div>
                  ))}
              </AnimatePresence>
            </div>
          ))}
          
          {books.length === 0 && (
            <div className="absolute inset-0 flex flex-col items-center justify-center opacity-10 pointer-events-none">
              <BookOpen size={48} className="mb-2" />
              <p className="text-[10px] font-bold uppercase tracking-tighter">Your library is empty</p>
            </div>
          )}
        </div>

        {/* Global Progress */}
        <div className="absolute bottom-2 right-4">
           <p className="text-[10px] font-bold text-on-surface-variant uppercase">
             {books.length} / 15 slots
           </p>
        </div>
      </div>
    </div>
  );
};
