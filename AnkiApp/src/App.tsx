import { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Settings, 
  Library, 
  Layers, 
  BarChart3, 
  Play,
  Key
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { RobotDesk } from './components/RobotDesk';
import type { RobotState } from './components/RobotDesk';
import { AnimatedLibrary } from './components/AnimatedLibrary';
import { TerminalDrawer } from './components/TerminalDrawer';
import { DecksView } from './components/DecksView';

const navItems = [
  { name: 'Workspace', icon: Library },
  { name: 'Decks', icon: Layers },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('Workspace');
  const [learningDepth, setLearningDepth] = useState('Zero lecture');
  const [status, setStatus] = useState<RobotState>('idle');
  const [stageProgress, setStageProgress] = useState(0);
  const [stageStatusText, setStageStatusText] = useState('Système en attente');
  const [currentStage, setCurrentStage] = useState(0);
  const [books, setBooks] = useState<any[]>([]);
  const [isSyncing, setIsSyncing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // API Key & Refresh state
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [isSavingKey, setIsSavingKey] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  // Terminal drawer state
  const [isTerminalOpen, setIsTerminalOpen] = useState(false);

  useEffect(() => {
    const fetchBooks = () => {
      // @ts-ignore
      if (window.pywebview?.api?.get_library_books) {
        // @ts-ignore
        window.pywebview.api.get_library_books().then((fetchedBooks) => {
          if (fetchedBooks && Array.isArray(fetchedBooks)) {
            setBooks(fetchedBooks);
          }
        }).catch(console.error);
      }
    };

    const initApp = async () => {
      // @ts-ignore
      if (window.pywebview?.api?.check_api_key) {
        // @ts-ignore
        const hasKey = await window.pywebview.api.check_api_key();
        if (!hasKey) {
          setShowApiKeyModal(true);
        }
      }
      fetchBooks();
    };

    window.addEventListener('pywebviewready', initApp);
    // Call it immediately just in case pywebview is already ready
    if ((window as any).pywebview) {
      initApp();
    }

    // Expose global functions for pywebview backend
    // @ts-ignore
    window.receiveProgress = (stage: number, text: string, ratio: number) => {
      setCurrentStage(stage);
      setStageProgress(ratio);
      setStageStatusText(text);

      const textLower = text.toLowerCase();
      if (textLower.includes('fusion')) {
        setStatus('fusion');
      } else if (textLower.includes('pont')) {
        setStatus('bridge_generation');
      } else if (textLower.includes('doublon') && stage === 3) {
        setStatus('sort');
      } else if (stage === 1) {
        setStatus('reading');
      } else if (stage === 2) {
        setStatus('generation');
      } else if (stage === 4) {
        setStatus('bridge_generation');
      }
    };

    // @ts-ignore
    window.receiveLog = (message: string) => {
      setLogs(prev => [...prev, message]);
    };

    // @ts-ignore
    window.onProcessingComplete = () => {
      setIsProcessing(false);
      setStatus('transporting');
      setStageStatusText('Génération terminée ! Rangement du deck...');
      setStageProgress(1);
      setIsSyncing(true);
      
      setTimeout(() => {
        const resetState = () => {
           setStatus('idle');
           setIsSyncing(false);
           setStageStatusText('Système en attente');
           setStageProgress(0);
           setCurrentStage(0);
        };

        // Refresh books list to get the new deck
        // @ts-ignore
        if (window.pywebview?.api?.get_library_books) {
          // @ts-ignore
          window.pywebview.api.get_library_books().then((fetchedBooks) => {
             setBooks(fetchedBooks || []);
             resetState();
          }).catch(() => resetState());
        } else {
          resetState();
        }
      }, 3500); // Wait for transport animation
    };

    // @ts-ignore
    window.onProcessingError = (error: string) => {
      setIsProcessing(false);
      setStatus('idle');
      setStageStatusText(`Erreur : ${error}`);
      setLogs(prev => [...prev, `[ERROR] ${error}`]);
    };

    return () => {
      window.removeEventListener('pywebviewready', initApp);
      // @ts-ignore
      delete window.receiveProgress;
      // @ts-ignore
      delete window.receiveLog;
      // @ts-ignore
      delete window.onProcessingComplete;
      // @ts-ignore
      delete window.onProcessingError;
    };
  }, [refreshKey]);

  const handleSaveApiKey = async () => {
    setIsSavingKey(true);
    // @ts-ignore
    if (window.pywebview?.api?.save_api_key) {
      // @ts-ignore
      const success = await window.pywebview.api.save_api_key(apiKeyInput.trim());
      if (success) {
        setShowApiKeyModal(false);
      } else {
        alert("Erreur lors de la sauvegarde de la clé API.");
      }
    } else {
      // Fallback for dev mode
      setShowApiKeyModal(false);
    }
    setIsSavingKey(false);
  };

  const startProcessing = () => {
    if (isProcessing) return;
    
    // @ts-ignore
    if (window.pywebview) {
      // @ts-ignore
      window.pywebview.api.choose_file().then((filePath: string | null) => {
         if (filePath) {
            setIsProcessing(true);
            setLogs([]);
            setStatus('idle');
            setStageStatusText('Initialisation...');
            setStageProgress(0);
            setCurrentStage(0);
            
            // @ts-ignore
            window.pywebview.api.start_processing(filePath, learningDepth).catch((err: any) => {
              setIsProcessing(false);
              setStageStatusText(`Erreur de lancement : ${err}`);
            });
         }
      });
    } else {
      // Mode Dev/Demo React seul
      setIsProcessing(true);
      setStatus('reading');
      setStageStatusText('Simulation : Lecture en cours...');
      let progress = 0;
      
      const interval = setInterval(() => {
        progress += 0.2;
        setStageProgress(progress);
        if (progress >= 1) {
          clearInterval(interval);
          // @ts-ignore
          if (window.onProcessingComplete) window.onProcessingComplete();
        }
      }, 1000);
    }
  };

  const toggleTerminal = () => {
    setIsTerminalOpen(prev => !prev);
  };

  return (
    <div className="min-h-screen flex flex-col font-sans relative overflow-hidden bg-surface">
      {/* Top Navigation */}
      <header className="bg-surface-container-lowest border-b-2 border-surface-container-highest sticky top-0 z-50 h-20 px-6 md:px-10 flex items-center justify-between max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-12">
          <div className="flex items-center gap-3">
             <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white rotate-6 shadow-lg">
                <Bot size={24} />
             </div>
             <span className="text-2xl font-extrabold text-primary tracking-tighter uppercase">
               Anki Robot
             </span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <button
                key={item.name}
                onClick={() => setActiveTab(item.name)}
                className={`relative py-2 text-sm font-bold transition-colors hover:text-primary ${
                  activeTab === item.name ? 'text-primary' : 'text-on-surface-variant'
                }`}
              >
                {item.name}
                {activeTab === item.name && (
                  <motion.div
                    layoutId="activeTab"
                    className="absolute -bottom-1 left-0 right-0 h-1 bg-primary rounded-t-full"
                  />
                )}
              </button>
            ))}
          </nav>
        </div>
        
        {/* Top-right icons removed as requested */}
      </header>

      {/* Main Content */}
      <main className="flex-grow w-full max-w-7xl mx-auto px-6 md:px-10 py-8 flex flex-col gap-8 relative z-10">
        
        {activeTab === 'Decks' ? (
          <DecksView books={books} onRefreshRequested={() => setRefreshKey(k => k + 1)} />
        ) : (
          <>
            {/* Unified Scene: Library in background, Robot in foreground */}
            <div className="w-full h-[550px] bg-surface-container-lowest rounded-3xl shadow-sm border border-surface-container-highest relative overflow-hidden flex flex-col justify-end perspective-[1000px]">
              
              {/* Background: Animated Library */}
              <div className="absolute top-4 right-10 w-96 h-[80%] opacity-90 z-0">
                <AnimatedLibrary books={books.slice(-15)} isSyncing={isSyncing} onBookClick={(id) => {
                  // @ts-ignore
                  if (window.pywebview?.api?.open_deck_folder) window.pywebview.api.open_deck_folder(id);
                }} />
              </div>
              
              {/* Foreground: Robot Desk */}
              <div className="w-full h-full relative z-10 pointer-events-none">
                 {/* the SVG will be absolutely positioned inside RobotDesk */}
                 <RobotDesk 
                   state={status} 
                   stageProgress={stageProgress}
                   stageStatusText={stageStatusText}
                 />
              </div>

            </div>

            {/* Bottom Controls */}
            <div className="flex flex-col md:flex-row gap-6">
              <div className="flex-1 bg-surface-container-lowest rounded-3xl p-8 flex flex-col justify-center border border-surface-container-highest shadow-sm relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-bl-[100px] -z-10 group-hover:scale-110 transition-transform duration-500" />
                
                <h2 className="text-2xl font-black tracking-tight text-on-surface mb-2">
                  Lancer la <span className="text-primary">Génération</span>
                </h2>
                <p className="text-on-surface-variant font-medium mb-6">
                  Le robot est prêt à transformer vos documents PDF. Un explorateur de fichiers va s'ouvrir.
                </p>
                
                <button
                  onClick={startProcessing}
                  disabled={isProcessing}
                  className="w-full md:w-auto self-start bg-primary hover:bg-primary-dark text-white rounded-2xl px-8 py-4 font-bold text-lg flex items-center gap-3 transition-all active:scale-95 shadow-md shadow-primary/20 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Play size={24} fill="currentColor" />
                  {isProcessing ? 'En cours...' : 'Démarrer le processus'}
                </button>
              </div>
            </div>

            {/* Debug buttons removed as requested */}
          </>
        )}
      </main>

      {/* API Key Modal */}
      <AnimatePresence>
        {showApiKeyModal && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl border border-neutral-100 flex flex-col gap-6"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                  <Key size={24} />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-neutral-800">Bienvenue !</h2>
                  <p className="text-sm text-neutral-500 font-medium">Configuration initiale</p>
                </div>
              </div>
              
              <div className="text-neutral-600 text-sm leading-relaxed">
                <p className="mb-4">
                  Pour que le robot puisse générer vos cartes Anki, il a besoin d'accéder au modèle d'intelligence artificielle Mistral.
                </p>
                <p>
                  Veuillez entrer votre <strong>Clé API Mistral</strong>. Elle sera sauvegardée localement de manière sécurisée.
                </p>
              </div>

              <div className="flex flex-col gap-2">
                <input 
                  type="password"
                  placeholder="Votre clé API Mistral..."
                  value={apiKeyInput}
                  onChange={(e) => setApiKeyInput(e.target.value)}
                  className="w-full px-4 py-3 bg-neutral-50 border border-neutral-200 rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary font-mono text-sm transition-all"
                  autoFocus
                />
              </div>

              <button 
                onClick={handleSaveApiKey}
                disabled={!apiKeyInput.trim() || isSavingKey}
                className="w-full py-3 bg-primary hover:bg-primary-dark text-white rounded-xl font-bold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isSavingKey ? 'Sauvegarde...' : 'Enregistrer la clé'}
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Terminal Drawer for Logs */}
      <TerminalDrawer 
        isOpen={isTerminalOpen} 
        onClose={() => setIsTerminalOpen(false)} 
        logs={logs} 
        currentStage={currentStage} 
      />
    </div>
  );
}
