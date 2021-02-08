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
            contentsMenuWidth: number;
            headerHeight: number;
            footerHeight: number;
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
            contentsMenuWidth: 240,
            headerHeight: 64,
            footerHeight: 80,
        },
    });
}
