import { motion, AnimatePresence } from 'framer-motion';
import { BookOpen, Search, ChevronLeft, ChevronRight, Trash2, X } from 'lucide-react';
import { useState, useRef } from 'react';
import { TrashCan } from './TrashCan';

// Extend the global Window interface for Pywebview
declare global {
  interface Window {
    pywebview?: {
      api?: {
        open_deck_folder: (folderName: string) => void;
        delete_deck_folder: (folderName: string) => Promise<boolean>;
      }
    }
  }
}

interface Deck {
  id: string;
  title: string;
  color: string;
  position: number;
}

interface DecksViewProps {
  books: Deck[];
  onRefreshRequested: () => void;
}

export const DecksView = ({ books, onRefreshRequested }: DecksViewProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [mouseX, setMouseX] = useState(0);
  const [trashedBooks, setTrashedBooks] = useState<Deck[]>([]);
  const [fallingBook, setFallingBook] = useState<{ id: string; targetX: number; targetY: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDeleting && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setMouseX(e.clientX - rect.left);
    }
  };

  const handleBookClick = async (book: Deck, e: React.MouseEvent) => {
    e.stopPropagation();
    if (isDeleting) {
      if (containerRef.current && e.currentTarget) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const bookRect = e.currentTarget.getBoundingClientRect();
        
        // Exact center offsets
        const bookCenterX = bookRect.left + bookRect.width / 2 - containerRect.left;
        const targetX = mouseX - bookCenterX;
        
        const bookCenterY = bookRect.top + bookRect.height / 2 - containerRect.top;
        const targetY = containerRect.height - bookCenterY - 70; // Aim for the hole

        setFallingBook({ id: book.id, targetX, targetY });
      } else {
        setFallingBook({ id: book.id, targetX: 0, targetY: 400 });
      }

      setTimeout(() => {
        setTrashedBooks(prev => [...prev, book]);
        setFallingBook(null);
      }, 500); // 500ms fall duration
    } else {
      if (window.pywebview?.api?.open_deck_folder) {
        window.pywebview.api.open_deck_folder(book.id);
      }
    }
  };

  const handleRestore = (id: string) => {
    setTrashedBooks(prev => prev.filter(b => b.id !== id));
  };

  const handleFinalDelete = async () => {
    if (window.pywebview?.api?.delete_deck_folder) {
      for (const book of trashedBooks) {
        await window.pywebview.api.delete_deck_folder(book.id);
      }
      onRefreshRequested();
    }
    setTrashedBooks([]);
    setIsDeleting(false);
  };

  const visibleBooks = books.filter(b => !trashedBooks.find(tb => tb.id === b.id));
  const filteredDecks = visibleBooks.filter(d => 
    d.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Pagination Logic
  const BOOKS_PER_SHELF = 10;
  const SHELVES_PER_PAGE = 4;
  const BOOKS_PER_PAGE = BOOKS_PER_SHELF * SHELVES_PER_PAGE;

  const totalPages = Math.ceil(filteredDecks.length / BOOKS_PER_PAGE) || 1;
  
  if (currentPage >= totalPages && totalPages > 0) {
    setCurrentPage(0);
  }

  const handleNextPage = () => {
    if (currentPage < totalPages - 1) setCurrentPage(p => p + 1);
  };

  const handlePrevPage = () => {
    if (currentPage > 0) setCurrentPage(p => p - 1);
  };

  const currentBooks = filteredDecks.slice(currentPage * BOOKS_PER_PAGE, (currentPage + 1) * BOOKS_PER_PAGE);

  // Distribute books into 5 shelves
  const shelves = [];
  for (let i = 0; i < SHELVES_PER_PAGE; i++) {
    shelves.push(currentBooks.slice(i * BOOKS_PER_SHELF, (i + 1) * BOOKS_PER_SHELF));
  }

  const getBookHeight = (id: string, idx: number) => {
    const heights = ['h-[85px]', 'h-[100px]', 'h-[110px]', 'h-[125px]', 'h-[95px]'];
    const sum = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return heights[(sum + idx) % heights.length];
  };

  const formatBookTitle = (title: string) => {
    // Strips out dates (YYYY-MM-DD, HH-MM-SS, etc)
    let cleaned = title.replace(/\d{4}-\d{2}-\d{2}/g, '')
                       .replace(/\d{2}-\d{2}-\d{2}/g, '')
                       .replace(/\d{8}_\d{6}/g, '')
                       .replace(/_/g, ' ')
                       .trim();
    cleaned = cleaned.replace(/^-+|-+$/g, '').trim();
    return cleaned || "DECK";
  };

  return (
    <div 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className="bg-[#FAF8F5] rounded-3xl p-8 shadow-sm flex flex-col h-full min-h-[700px] border border-neutral-200/50 relative overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-[#8B5A2B]/10 rounded-xl flex items-center justify-center">
            <BookOpen className="text-[#8B5A2B]" size={24} />
          </div>
          <div>
            <h2 className="text-2xl font-extrabold text-neutral-800 tracking-tight">Grande Bibliothèque</h2>
            <p className="text-sm text-neutral-500 font-medium">Page {currentPage + 1} sur {totalPages} • {filteredDecks.length} decks</p>
          </div>
        </div>

        <div className="flex items-center gap-4 relative">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={18} />
            <input 
              type="text" 
              placeholder="Rechercher un deck..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-3 bg-white border border-neutral-200 rounded-xl focus:outline-none focus:border-[#8B5A2B] focus:ring-1 focus:ring-[#8B5A2B] w-64 text-sm font-medium transition-all shadow-sm"
            />
          </div>
          {trashedBooks.length > 0 && (
            <button
              onClick={handleFinalDelete}
              className="flex items-center gap-2 px-4 py-3 rounded-xl font-bold transition-all shadow-sm bg-red-600 text-white hover:bg-red-700 border border-red-700 animate-pulse"
            >
              <Trash2 size={18} /> Jeter définitivement ({trashedBooks.length})
            </button>
          )}

          <button
            onClick={() => {
              if (isDeleting) {
                setTrashedBooks([]);
                setIsDeleting(false);
              } else {
                setIsDeleting(true);
              }
            }}
            className={`flex items-center gap-2 px-4 py-3 rounded-xl font-bold transition-all shadow-sm ${
              isDeleting 
                ? 'bg-neutral-800 text-white hover:bg-neutral-900 border border-neutral-900' 
                : 'bg-red-50 text-red-600 hover:bg-red-100 border border-red-200'
            }`}
          >
            {isDeleting ? (
              <>
                <X size={18} /> Annuler
              </>
            ) : (
              <>
                <Trash2 size={18} /> Supprimer
              </>
            )}
          </button>
        </div>
      </div>

      {/* Kiosk / Carousel Area */}
      <div className="relative flex-grow flex items-center justify-center px-12">
        
        {/* Left Arrow */}
        <AnimatePresence>
          {currentPage > 0 && (
            <motion.button 
              initial={{ opacity: 0, x: 20 }} 
              animate={{ opacity: 1, x: 0 }} 
              exit={{ opacity: 0, x: 20 }}
              onClick={handlePrevPage}
              className="absolute left-0 z-30 p-4 bg-white/90 backdrop-blur-md rounded-full shadow-xl text-neutral-600 hover:text-[#8B5A2B] hover:scale-110 transition-all border border-neutral-100"
            >
              <ChevronLeft size={32} />
            </motion.button>
          )}
        </AnimatePresence>

        {/* Right Arrow */}
        <AnimatePresence>
          {currentPage < totalPages - 1 && (
            <motion.button 
              initial={{ opacity: 0, x: -20 }} 
              animate={{ opacity: 1, x: 0 }} 
              exit={{ opacity: 0, x: -20 }}
              onClick={handleNextPage}
              className="absolute right-0 z-30 p-4 bg-white/90 backdrop-blur-md rounded-full shadow-xl text-neutral-600 hover:text-[#8B5A2B] hover:scale-110 transition-all border border-neutral-100"
            >
              <ChevronRight size={32} />
            </motion.button>
          )}
        </AnimatePresence>

        {/* The Bookshelf */}
        <div className="w-full max-w-4xl flex flex-col bg-[#F4EBE1] border-[14px] border-[#5C3A21] rounded-sm relative shadow-2xl mt-4 mb-24">
          {/* Inner wall shadow */}
          <div className="absolute inset-0 shadow-[inset_0_0_60px_rgba(0,0,0,0.15)] pointer-events-none"></div>
          
          {shelves.map((shelfBooks, shelfIndex) => (
            <div key={shelfIndex} className="relative w-full flex flex-col justify-end" style={{ height: '140px' }}>
              {/* Books Container */}
              <div className="flex items-end gap-3 px-8 pb-0 relative z-10" style={{ height: '120px' }}>
                {shelfBooks.map((book, idx) => {
                  const isFalling = fallingBook?.id === book.id;
                  return (
                  <motion.div 
                    key={book.id}
                    animate={isFalling ? { x: fallingBook.targetX, y: fallingBook.targetY, scale: 0.3, rotate: 180 } : { x: 0, y: 0, scale: 1, rotate: 0 }}
                    transition={isFalling ? { duration: 0.5, ease: "easeIn" } : { type: "spring" }}
                    whileHover={isFalling ? undefined : (isDeleting ? { y: -5, scale: 1.05 } : { y: -15, rotate: -2, scale: 1.05 })}
                    onClick={(e) => handleBookClick(book, e)}
                    className={`relative cursor-pointer group`}
                    style={{ zIndex: isFalling ? 99 : 20 + idx }}
                  >
                    {/* Book Spine */}
                    <div 
                      className={`w-14 ${getBookHeight(book.id, idx)} rounded-sm shadow-[4px_4px_10px_rgba(0,0,0,0.4)] relative overflow-hidden`} 
                      style={{ backgroundColor: book.color }}
                    >
                      <div className="absolute inset-y-0 left-1.5 w-1 bg-white/30"></div>
                      <div className="absolute inset-y-0 right-0 w-2 bg-black/20"></div>
                      <div className="absolute top-3 left-0 right-0 h-0.5 bg-white/40"></div>
                      <div className="absolute bottom-3 left-0 right-0 h-0.5 bg-white/40"></div>
                      
                      <div className="absolute inset-0 py-5 px-1 flex items-center justify-center pointer-events-none">
                         <span 
                           className="text-white/80 text-[9px] font-bold tracking-widest uppercase leading-snug text-center overflow-hidden" 
                           style={{ 
                             writingMode: 'vertical-rl', 
                             transform: 'rotate(180deg)',
                             maxHeight: '100%'
                           }}
                         >
                            {formatBookTitle(book.title)}
                         </span>
                      </div>
                    </div>

                    {/* Hover Tooltip */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none bg-[#1F2937] text-white text-sm font-bold px-4 py-2 rounded-lg whitespace-nowrap shadow-2xl z-50 border border-white/10">
                      {book.title}
                      <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-[#1F2937]"></div>
                    </div>
                  </motion.div>
                  );
                })}
              </div>
              
              {/* Shelf Base (Wood Plank) */}
              <div className="h-[20px] bg-[#8B5A2B] border-t-2 border-[#A67B5B] border-b-4 border-[#4A2F1D] shadow-[0_12px_15px_-5px_rgba(0,0,0,0.5)] relative z-20"></div>
            </div>
          ))}
        </div>

        {/* Floating Trash Can */}
        <AnimatePresence>
          {isDeleting && (
            <motion.div
              initial={{ y: 150, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 150, opacity: 0 }}
              className="absolute bottom-4 left-0 pointer-events-none z-50"
              style={{ x: mouseX - 105 }} // Shifted slightly right to center the hole visually against the lid weight
            >
              <TrashCan 
                isDeleting={true} 
                trashedBooks={trashedBooks}
                onRestore={handleRestore}
              />
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </div>
  );
};
