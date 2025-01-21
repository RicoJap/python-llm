import { createTheme } from '@mui/material/styles';
import { AppProvider, type Navigation } from '@toolpad/core/AppProvider';
import { DashboardLayout } from '@toolpad/core/DashboardLayout';
import { useDemoRouter } from '@toolpad/core/internal';
import AssistantIcon from '@mui/icons-material/Assistant';
import ViewListIcon from '@mui/icons-material/ViewList';
import PageContent from './components/PageContent';
import GeneratedSelectors from './components/GeneratedSelectors';
import SelectorsList from './components/SelectorsList';

const NAVIGATION: Navigation = [
  {
    kind: 'header',
    title: 'Main items',
  },
  {
    segment: 'add-forms',
    title: 'Add forms',
    icon: <AssistantIcon />,
  },
  {
    kind: 'divider',
  },
  {
    segment: 'forms-list',
    title: 'Forms List',
    icon: <ViewListIcon />,
  },
  {
    kind: 'header',
    title: 'Settings',
  },
];

const demoTheme = createTheme({
  cssVariables: {
    colorSchemeSelector: 'data-toolpad-color-scheme',
  },
  colorSchemes: { light: true, dark: true },
  breakpoints: {
    values: {
      xs: 0,
      sm: 600,
      md: 600,
      lg: 1200,
      xl: 1536,
    },
  },
});



interface DemoProps {
  /**
   * Injected by the documentation to work in an iframe.
   * Remove this when copying and pasting into your project.
   */
  window?: () => Window;
}

export default function DashboardLayoutBasic(props: DemoProps) {
  const { window } = props;

  const router = useDemoRouter('/llm-generated-selectors');

  // Remove this const when copying and pasting into your project.
  const demoWindow = window !== undefined ? window() : undefined;

  const renderPageContents = () => {
    if(router.pathname === '/add-forms') {
      return <GeneratedSelectors />;
    } else if(router.pathname === '/forms-list') {
      return <SelectorsList />;
    }
  }

  return (
    <AppProvider
      navigation={NAVIGATION}
      router={router}
      theme={demoTheme}
      window={demoWindow}
    >
      <DashboardLayout defaultSidebarCollapsed branding={{title: 'Form Automation'}}>
        <PageContent>
          {renderPageContents()}
        </PageContent>
      </DashboardLayout>
    </AppProvider>
  );
}
