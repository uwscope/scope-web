export const getTodayString = () => {
    return `Today is ${new Date().toLocaleDateString('en-us', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    })}`;
};
