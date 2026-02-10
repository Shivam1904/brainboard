import { DEFAULT_TIMEZONE, TIMEZONE_CONFIG } from '../constants/time';

/**
 * Returns the current date/time adjusted to the configured timezone.
 * Note: This creates a Date object where the internal UTC time matches the
 * wall-clock time in the target timezone. This is useful for comparisons
 * but should be used carefully when sending dates back to a server.
 */
export const getCurrentTimeInZone = (): Date => {
    const now = new Date();
    return getZoneTime(now);
};

/**
 * Converts a Date object to the configured timezone's wall-clock time.
 */
export const getZoneTime = (date: Date): Date => {
    const timeString = date.toLocaleString('en-US', { timeZone: DEFAULT_TIMEZONE });
    return new Date(timeString);
};

export const formatDate = (date: Date | string | number, options?: Intl.DateTimeFormatOptions): string => {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        ...TIMEZONE_CONFIG,
        ...options,
    });
};

export const formatTime = (date: Date | string | number, options?: Intl.DateTimeFormatOptions): string => {
    const d = new Date(date);
    return d.toLocaleTimeString('en-US', {
        ...TIMEZONE_CONFIG,
        ...options,
    });
};

export const formatDateTime = (date: Date | string | number, options?: Intl.DateTimeFormatOptions): string => {
    const d = new Date(date);
    return d.toLocaleString('en-US', {
        ...TIMEZONE_CONFIG,
        ...options,
    });
};

/**
 * Creates a Date object from a date string (YYYY-MM-DD) treating it as local to the timezone.
 */
export const parseDateInZone = (dateStr: string): Date => {
    // Append midnight time to ensure it parses as local date
    const timeStr = `${dateStr}T00:00:00`;
    const date = new Date(timeStr);
    // This is a naive implementation; for robust parsing considering timezone offsets precisely,
    // libraries like date-fns-tz or luxon are recommended.
    // For now, we assume standard browser parsing handles local context or we rely on the
    // fact that we want to treat this "as if" it's in our zone.
    return date;
};
export const getTodayDateString = (): string => {
    const now = new Date();
    return toLocalISOString(now);
};

export const toLocalISOString = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

export const addDays = (dateStr: string, days: number): string => {
    const date = new Date(`${dateStr}T12:00:00`); // Use noon to avoid DST edge cases
    date.setDate(date.getDate() + days);
    return toLocalISOString(date);
};
