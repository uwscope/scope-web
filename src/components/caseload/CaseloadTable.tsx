import { observer } from 'mobx-react';
import MUIDataTable, { MUIDataTableColumnDef, MUIDataTableOptions } from 'mui-datatables';
import React, { FunctionComponent } from 'react';
import { IPatientStore } from 'src/stores/PatientStore';

export interface ICaseloadTableProps {
    patients: ReadonlyArray<IPatientStore>;
    onPatientClick?: (mrn: string) => void;
}

export const CaseloadTable: FunctionComponent<ICaseloadTableProps> = observer((props) => {
    const { patients, onPatientClick } = props;

    const onRowClick = (rowData: string[]) => {
        if (!!onPatientClick) {
            onPatientClick(rowData[0]);
        }
    };

    // Column names map to IPatientStore property names
    const columns = [
        { name: 'MRN', label: 'MRN', options: { filter: false } },
        { name: 'name', label: 'Name', options: { filter: false } },
        { name: 'depressionTreatmentStatus', label: 'Depression Treatment Status' },
        { name: 'clinicCode', label: 'Clinic Code' },
        { name: 'followupSchedule', label: 'Follow-up Schedule' },
    ] as MUIDataTableColumnDef[];

    const data = patients.map((p) => Object.assign({}, p));

    const options = {
        filterType: 'checkbox',
        selectableRows: 'none',
        onRowClick: onRowClick,
    } as MUIDataTableOptions;

    return (
        <div>
            <MUIDataTable title={'Patients'} data={data} columns={columns} options={options}></MUIDataTable>
        </div>
    );
});

export default CaseloadTable;
