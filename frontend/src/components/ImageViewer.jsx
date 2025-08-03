// src/components/ImageViewer.jsx
import React, { useRef, useEffect, useState } from 'react';
import { Stage, Layer, Image, Rect, Text } from 'react-konva';
import useImage from 'use-image';

const ImageViewer = ({ imageUrl, bounds, hoveredId }) => {
  const [image] = useImage(imageUrl, 'Anonymous');
  const containerRef = useRef(null);
  const [stageSize, setStageSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const checkSize = () => {
      if (containerRef.current) {
        setStageSize({ width: containerRef.current.offsetWidth, height: containerRef.current.offsetHeight });
      }
    };
    checkSize();
    window.addEventListener('resize', checkSize);
    return () => window.removeEventListener('resize', checkSize);
  }, []);

  let imageScale = 1;
  if (image && stageSize.width > 0 && stageSize.height > 0) {
    const scaleX = stageSize.width / image.width;
    const scaleY = stageSize.height / image.height;
    imageScale = Math.min(scaleX, scaleY);
  }

  return (
    <div ref={containerRef} className="w-full h-full bg-white shadow-inner rounded-lg overflow-hidden">
      <Stage width={stageSize.width} height={stageSize.height} draggable>
        <Layer scaleX={imageScale} scaleY={imageScale}>
          {image && <Image image={image} />}
          {bounds.map(b => {
            const { xmin, ymin, xmax, ymax } = b.position;
            const isHovered = b.id === hoveredId; // Kiểm tra có đang hover không

            return (
              <React.Fragment key={b.id}>
                <Rect
                  x={xmin} y={ymin}
                  width={xmax - xmin} height={ymax - ymin}
                  stroke={b.color}
                  strokeWidth={isHovered ? 5 / imageScale : 3 / imageScale} // Hiệu ứng đường viền
                  shadowColor="black"
                  shadowBlur={isHovered ? 15 / imageScale : 5 / imageScale} // Hiệu ứng bóng đổ
                  shadowOpacity={isHovered ? 0.9 : 0.7}
                />
                <Text
                  text={`${b.class_name}: ${Math.round(b.confidence * 100)}%`}
                  x={xmin}
                  y={ymin - (20 / imageScale)}
                  fontSize={14 / imageScale}
                  fill="white"
                  padding={5 / imageScale}
                  backgroundColor={b.color}
                  cornerRadius={4}
                />
              </React.Fragment>
            );
          })}
        </Layer>
      </Stage>
    </div>
  );
};

export default ImageViewer;