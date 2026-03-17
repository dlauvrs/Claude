'use client';

import Image from 'next/image';

interface ImageGalleryProps {
  photoUrls: string[];
  selectedIndex?: number;
  onSelect?: (index: number) => void;
}

export function ImageGallery({ photoUrls, selectedIndex = 0, onSelect }: ImageGalleryProps) {
  if (!photoUrls.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg bg-gray-100 text-gray-400">
        Sem fotos
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="relative aspect-square w-full overflow-hidden rounded-lg bg-gray-100">
        <Image
          src={photoUrls[selectedIndex]}
          alt={`Foto ${selectedIndex + 1}`}
          fill
          className="object-contain"
          unoptimized
        />
        <span className="absolute right-2 top-2 rounded bg-black/50 px-2 py-1 text-xs text-white">
          {selectedIndex + 1} / {photoUrls.length}
        </span>
      </div>
      {photoUrls.length > 1 && (
        <div className="flex gap-2 overflow-x-auto pb-1">
          {photoUrls.map((url, i) => (
            <button
              key={i}
              onClick={() => onSelect?.(i)}
              className={`relative h-16 w-16 flex-shrink-0 overflow-hidden rounded border-2 transition ${
                i === selectedIndex ? 'border-blue-500' : 'border-transparent'
              }`}
            >
              <Image src={url} alt={`Miniatura ${i + 1}`} fill className="object-cover" unoptimized />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
