import { create } from 'zustand';

export type Form = {
  name: string;
  url: string;
  selectors: {label: string, value: string}[];
}[];

export type SelectorStoreTypes = {
  forms: Form;
  actions: {
    setForms: (forms: Form) => void;
  }
};

const initialState = {
  forms: []
}

const store = create<SelectorStoreTypes>(set => ({
  ...initialState,
  actions: {
    setForms: (forms: Form) => set({ forms }),
  },
}));

// State
export const useForms = (): Form => store(state => state.forms);

// Actions
export const useSelectorStoreActions = (): SelectorStoreTypes['actions'] => store(state => state.actions);