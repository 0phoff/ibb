import { VBoxModel, VBoxView } from '@jupyter-widgets/controls';
import '../css/maincontainer.css';
export declare class MainContainerModel extends VBoxModel {
    static model_name: string;
    static model_module: any;
    static model_module_version: any;
    static view_name: string;
    static view_module: any;
    static view_module_version: any;
    defaults(): any;
}
export declare class MainContainerView extends VBoxView {
    initialize(parameters: any): void;
}
