import { amber, teal } from '@mui/material/colors';
import { createTheme } from '@mui/material/styles';
import React from 'react';

declare module '@mui/material/styles' {
    interface Theme {
        customPalette: {
            subtle: React.CSSProperties['color'];
            discrete10: string[];
            panel: React.CSSProperties['color'];
        };
        customSizes: {
            drawerWidth: number;
            contentsMenuWidth: number;
            headerHeight: number;
            footerHeight: number;
        };
    }
    interface ThemeOptions {
        customPalette: {
            subtle: React.CSSProperties['color'];
            discrete10: string[];
            panel: React.CSSProperties['color'];
        };
        customSizes: {
            drawerWidth: number;
            contentsMenuWidth: number;
            headerHeight: number;
            footerHeight: number;
        };
    }
}

declare module '@mui/system/createTheme/createBreakpoints' {
    interface BreakpointOverrides {
        xs: false; // removes the `xs` breakpoint
        sm: false;
        md: false;
        lg: false;
        xl: false;
        phone: true;
        tablet: true;
        laptop: true;
        desktop: true;
    }
}

export default function createAppTheme() {
    return createTheme({
        palette: { primary: teal, secondary: amber },
        typography: {
            h5: {
                fontSize: '1.1rem',
                lineHeight: 1.1,
            },
            fontSize: 16,
        },
        customPalette: {
            subtle: '#eeeeee',
            panel: '#ffffffcc',
            discrete10: [
                '#1f77b4',
                '#ff7f0e',
                '#2ca02c',
                '#d62728',
                '#9467bd',
                '#8c564b',
                '#e377c2',
                '#7f7f7f',
                '#bcbd22',
                '#17becf',
            ],
        },
        customSizes: {
            drawerWidth: 240,
            contentsMenuWidth: 240,
            headerHeight: 64,
            footerHeight: 80,
        },
        breakpoints: {
            values: {
                phone: 360,
                tablet: 480,
                laptop: 1024,
                desktop: 1280,
            },
        },
    });
}
