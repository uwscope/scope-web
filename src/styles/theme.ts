import { createMuiTheme } from '@material-ui/core/styles';

declare module '@material-ui/core/styles/createMuiTheme' {
    interface Theme {
        customPalette: {
            subtle: React.CSSProperties['color'];
        };
        customSizes: {
            drawerWidth: number;
        };
    }
    interface ThemeOptions {
        customPalette: {
            subtle: React.CSSProperties['color'];
        };
        customSizes: {
            drawerWidth: number;
        };
    }
}

export default function createAppTheme() {
    return createMuiTheme({
        customPalette: {
            subtle: '#eeeeee',
        },
        customSizes: {
            drawerWidth: 240,
        },
    });
}
