import * as React from 'react';
import * as style from './style.css';

export namespace Home {
    export interface Props {

    }
}
export class Home extends React.Component<Home.Props> {
    constructor(props: Home.Props) {
        super(props);
    }

    render() {
        return (
            <div className={style.normal}>
                <h1>Home</h1>
            </div>
        );
    }
}
