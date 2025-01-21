import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import { useForms } from '../../stores/useSelectorStore';
import { Typography } from '@mui/material';

const SelectorsList = () => {
  const forms = useForms();
  return(
    <Box
      style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}
    >
      <Typography variant="h5"><strong>Saved Forms</strong></Typography>
      {forms.map((form, i) => {
        return (
          <Stack spacing={2} key={i}>
            <Paper style={{width: 500}}>
              <List>
                <ListItem>Name: <strong style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{form.name}</strong></ListItem>
                <ListItem>URL: <strong style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{form.url}</strong></ListItem>
                {form.selectors.map((selector, j) => {
                  return (
                    <ListItem key={j}>
                      {selector.label}: <strong style={{overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'}}>{selector.value}</strong>
                    </ListItem>
                  )
                })}
              </List>
            </Paper>
          </Stack>
        )
      })}
    </Box>
  )
}

export default SelectorsList