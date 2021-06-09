import { indigo } from '@material-ui/core/colors';
import { createMuiTheme } from '@material-ui/core/styles';

declare module '@material-ui/core/styles/createMuiTheme' {
    interface Theme {
        customPalette: {
            subtle: React.CSSProperties['color'];
            label: React.CSSProperties['color'];
            discrete10: string[];
            scoreColors: { [key: string]: string };
        };
        customSizes: {
            contentsMenuWidth: number;
            headerHeight: number;
            footerHeight: number;
        };
    }
    interface ThemeOptions {
        customPalette: {
            subtle: React.CSSProperties['color'];
            label: React.CSSProperties['color'];
            discrete10: string[];
            scoreColors: { [key: string]: string };
        };
        customSizes: {
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
            label: '#00000088',
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
            scoreColors: {
                bad: '#bf2e2e',
                warning: '#ffbf00',
                good: '#20ab41',
                unknown: '#eee',
            },
        },
        customSizes: {
            contentsMenuWidth: 300,
            headerHeight: 64,
            footerHeight: 80,
        },
        overrides: {
            MuiFormLabel: {
                root: {
                    color: indigo[500],
                    textTransform: 'uppercase',
                    fontWeight: 700,
                },
            },
            MuiInput: {
                input: {
                    padding: '6px 12px',
                },
                inputMultiline: {
                    padding: '0 12px',
                },
                underline: {
                    background: '#fafafa',
                },
            },
            MuiFormControl: {
                root: {
                    paddingBottom: '24px',
                },
            },
            MuiCheckbox: {
                root: {},
            },
            MuiInputLabel: {
                shrink: {
                    transform: 'translate(0)',
                    fontSize: 14,
                    paddingBottom: 6,
                },
                formControl: {
                    transform: 'translate(0)',
                    fontSize: 14,
                    paddingBottom: 6,
                },
            },
            MuiFormControlLabel: {
                label: {
                    fontSize: 14,
                    paddingBottom: 0,
                },
            },
        },
    });
}
