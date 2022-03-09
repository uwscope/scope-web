import { indigo } from '@mui/material/colors';
import { createTheme } from '@mui/material/styles';

declare module '@mui/material/styles' {
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
            flagColors: { [key: string]: string };
        };
        customSizes: {
            contentsMenuWidth: number;
            headerHeight: number;
            footerHeight: number;
        };
    }
}

export default function createAppTheme() {
    return createTheme({
        palette: {
            primary: {
                main: '#3f51b5',
            },
            secondary: {
                main: '#f50057',
            },
        },
        typography: {
            body1: {
                fontSize: '0.8rem',
                lineHeight: 1.1,
            },
            body2: {
                fontSize: '0.8rem',
                lineHeight: 1,
            },
            h6: {
                fontSize: '0.9rem',
                lineHeight: 1.1,
            },
            h5: {
                fontSize: '1rem',
                lineHeight: 1.1,
            },
            h4: {
                fontSize: '1.2rem',
                lineHeight: 1.1,
            },
            fontSize: 12,
        },
        spacing: 4,
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
                bad: '#FFA29F',
                warning: '#FFF09F',
                good: '#8ADC98',
                unknown: '#fafafa',
                disabled: '#eeeeee',
            },
            flagColors: {
                safety: '#bf2e2e',
                discussion: '#ffbf00',
                disabled: '#eeeeee',
            },
        },
        customSizes: {
            contentsMenuWidth: 300,
            headerHeight: 48,
            footerHeight: 48,
        },
        components: {
            MuiList: {
                defaultProps: {
                    dense: true,
                },
            },
            MuiMenuItem: {
                defaultProps: {
                    dense: true,
                },
            },
            MuiTable: {
                defaultProps: {
                    size: 'small',
                },
            },
            MuiButton: {
                defaultProps: {
                    size: 'small',
                },
            },
            MuiButtonGroup: {
                defaultProps: {
                    size: 'small',
                },
            },
            MuiCheckbox: {
                defaultProps: {
                    size: 'small',
                },
                styleOverrides: {
                    root: {
                        padding: 4,
                    },
                },
            },
            MuiDialogContent: {
                styleOverrides: {
                    root: {
                        padding: 12,
                    },
                },
            },
            MuiDialogTitle: {
                styleOverrides: {
                    root: {
                        padding: 12,
                    },
                },
            },
            MuiDialogActions: {
                styleOverrides: {
                    root: {
                        padding: 12,
                    },
                },
            },
            MuiFab: {
                defaultProps: {
                    size: 'small',
                },
            },
            MuiFormControl: {
                styleOverrides: {
                    root: {},
                },
                defaultProps: {
                    margin: 'dense',
                    size: 'small',
                },
            },
            MuiFormControlLabel: {
                styleOverrides: {
                    label: {
                        paddingBottom: 0,
                    },
                },
            },
            MuiFormHelperText: {
                defaultProps: {
                    margin: 'dense',
                },
            },
            MuiFormLabel: {
                styleOverrides: {
                    root: {
                        color: indigo[500],
                        textTransform: 'uppercase',
                        fontWeight: 700,
                    },
                },
            },
            MuiIconButton: {
                defaultProps: {
                    size: 'small',
                },
            },
            MuiInput: {
                styleOverrides: {
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
            },
            MuiInputBase: {
                defaultProps: {
                    margin: 'dense',
                },
            },
            MuiInputLabel: {
                defaultProps: {
                    margin: 'dense',
                },
                styleOverrides: {
                    root: {
                        textTransform: 'none',
                    },
                    shrink: {
                        transform: 'translate(0)',
                        paddingBottom: 6,
                    },
                    formControl: {
                        transform: 'translate(0)',
                        paddingBottom: 6,
                    },
                },
            },
            MuiRadio: {
                defaultProps: {
                    size: 'small',
                },
                styleOverrides: {
                    root: {
                        padding: 4,
                    },
                },
            },
            MuiSwitch: {
                defaultProps: {
                    size: 'small',
                },
                styleOverrides: {
                    root: {
                        padding: 4,
                    },
                },
            },
            MuiTextField: {
                defaultProps: {
                    margin: 'dense',
                    size: 'small',
                },
            },
            MuiFormGroup: {
                styleOverrides: {
                    row: {
                        justifyContent: 'space-evenly',
                    },
                },
            },
        },
    });
}
