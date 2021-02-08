import { observer } from 'mobx-react';
import MUIDataTable, { MUIDataTableColumnDef, MUIDataTableOptions } from 'mui-datatables';
import React, { FunctionComponent } from 'react';
import { IPatientStore } from '../stores/PatientsStore';

export interface ICaseloadTableProps {
    patients: ReadonlyArray<IPatientStore>;
    onPatientClick?: (patient: IPatientStore) => void;
}

export const CaseloadTable: FunctionComponent<ICaseloadTableProps> = observer((props) => {
    const { patients } = props;

    // Column names map to IPatientStore property names
    const columns = [
        { name: 'mrn', label: 'MRN', options: { filter: false } },
        { name: 'name', label: 'Name', options: { filter: false } },
        { name: 'treatmentStatus', label: 'Treatment Status' },
        { name: 'clinicCode', label: 'Clinic Code' },
        { name: 'followupSchedule', label: 'Follow-up Schedule' },
        { name: 'discussionFlag', label: 'Discussion Flag' },
    ] as MUIDataTableColumnDef[];

    const data = patients.map((p) => Object.assign({}, p));

    const options = {
        filterType: 'checkbox',
        selectableRows: 'none',
    } as MUIDataTableOptions;

    return (
        <div>
            <MUIDataTable title={'Patients'} data={data} columns={columns} options={options}></MUIDataTable>
        </div>
    );
});

export default CaseloadTable;
