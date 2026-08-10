export const getDetectionColor = (label: string): string => {
  const normalizedLabel = label.toLowerCase();
  switch (normalizedLabel) {
    case 'person':
      return 'orange';
    case 'dog':
      return 'blue';
    case 'video':
      return 'transparent';
    default:
      return '#555';
  }
};
