import { format, formatDistanceToNow } from 'date-fns';

export function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return format(date, 'MMM d, yyyy');
}

export function formatTimeAgo(dateString: string): string {
    const date = new Date(dateString);
    return formatDistanceToNow(date, { addSuffix: true });
}

export function formatScore(score: number): string {
    return score.toFixed(1);
}

export function calculateScorePercentage(score: number, maxScore: number = 10): number {
    return (score / maxScore) * 100;
}

export function truncateText(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength - 3) + '...';
}