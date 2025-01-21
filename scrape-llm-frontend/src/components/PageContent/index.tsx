import Box from '@mui/material/Box';
import { PropsWithChildren, ReactElement } from 'react';

const PageContent = ({ children }: PropsWithChildren): ReactElement => {
  // const [data, setData] = useState(null);
  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       const response = await fetch('/api/selectors?url=https://www.diet-undeux.jp/contact-z/'); // Proxy will redirect to FastAPI
  //       if (!response.ok) {
  //         throw new Error('Failed to fetch data');
  //       }
  //       const result = await response.json();
  //       setData(result.css_selectors);
  //     } catch (error) {
  //       console.error('Error fetching data:', error);
  //     }
  //   };

  //   fetchData();
  // }, []);

  return (
    <Box
      sx={{
        p: 10,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
      }}
    >
      {children}
      {/* <Typography>Data: {JSON.stringify(data)}</Typography> */}
    </Box>
  );
}

export default PageContent;