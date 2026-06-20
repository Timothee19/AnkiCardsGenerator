import { motion } from 'motion/react';
import { UploadCloud } from 'lucide-react';

interface DropZoneProps {
  onDrop: () => void;
  isProcessing: boolean;
}

export const DropZone = ({ onDrop, isProcessing }: DropZoneProps) => {
  return (
    <motion.div 
      whileHover={!isProcessing ? { scale: 1.01 } : {}}
      whileTap={!isProcessing ? { scale: 0.99 } : {}}
      onClick={!isProcessing ? onDrop : undefined}
      className={`
        bg-surface-container-low border-2 border-dashed rounded-2xl p-12 
        flex flex-col items-center justify-center text-center transition-all
        ${isProcessing ? 'border-outline opacity-60 cursor-not-allowed' : 'border-secondary cursor-pointer hover:bg-surface-container'}
        relative overflow-hidden group
      `}
    >
      <motion.div 
        animate={isProcessing ? { y: [0, -10, 0] } : {}}
        transition={{ duration: 1, repeat: Infinity }}
        className="bg-secondary/10 p-5 rounded-full mb-4 group-hover:bg-secondary/20 transition-colors"
      >
        <UploadCloud size={48} className="text-secondary" />
      </motion.div>
      
      <h3 className="text-2xl font-bold text-on-surface mb-2">
        {isProcessing ? 'Processing PDF...' : 'Drop PDF Here'}
      </h3>
      <p className="text-on-surface-variant font-medium">
        {isProcessing ? 'Unit-01 is scanning your document' : 'or click to browse local files'}
      </p>

      {/* Background Pulse if processing */}
      {isProcessing && (
        <motion.div 
          className="absolute inset-0 bg-secondary/5"
          animate={{ opacity: [0, 0.2, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        />
      )}
    </motion.div>
  );
};
