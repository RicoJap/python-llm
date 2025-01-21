import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import LoadingButton from '@mui/lab/LoadingButton';
import Snackbar, { SnackbarCloseReason } from '@mui/material/Snackbar';
import Autocomplete from '@mui/material/Autocomplete';
import LoadingSpinner from '@mui/material/CircularProgress';
import IconButton from '@mui/material/IconButton';
import DeleteForeverIcon from '@mui/icons-material/DeleteForever';
import PsychologyIcon from '@mui/icons-material/Psychology';
import { Fragment, useState } from 'react';
import convertSelectorObjToArray from '../../utils/convertSelectorObjToArray';
import { Button, Typography } from '@mui/material';
import { useForms, useSelectorStoreActions } from '../../stores/useSelectorStore';

const GeneratedSelectors = () => {
  const [loading, setLoading] = useState(false);
  const [selectors, setSelectors] = useState<{label: string, value: string}[]>([]);
  const [selectorLabels, setSelectorLabels] = useState<string[]>([]);
  const [selectorValues, setSelectorValues] = useState<unknown[]>([]);
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [isDataFetched, setIsDataFetched] = useState(false);
  const [newSelector, setNewSelector] = useState<{label: string, value: string}>({label: '', value: ''});

  // Hooks
  const forms = useForms();
  const { setForms } = useSelectorStoreActions();

  const onGenerateClick = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/selectors?url=${url}`); // Proxy will redirect to FastAPI
      if (!response.ok) {
        throw new Error('Failed to fetch data');
      }
      const result = await response.json();
      setSelectors(convertSelectorObjToArray(result.css_selectors));
      setSelectorLabels(Object.keys(result.css_selectors));
      setSelectorValues(Object.values(result.css_selectors).filter(value => !!value));
      setLoading(false);
      setIsDataFetched(true);
    } catch (error) {
      const errMessage = `Error fetching data: ${error}`
      console.error(errMessage);
      setSelectors([]);
      setSelectorLabels([]);
      setSelectorValues([]);
      setSnackbarMessage(errMessage);
      setLoading(true);
      setIsDataFetched(false);
    }
  }

  const handleCloseSnackbar = (
    event: React.SyntheticEvent | Event,
    reason?: SnackbarCloseReason,
  ) => {
    if (reason === 'clickaway') {
      return;
    }

    setSnackbarOpen(false);
  };

  const onDeleteSelector = (selector: {label: string, value: string}) => {
    const filteredSelectors = selectors.filter((s) => s.label !== selector.label && s.value !== selector.value);
    setSelectors(filteredSelectors);
  }

  const onAddSelector = (selector: {label: string, value: string}) => {
    const newSelectors = [...selectors, selector];
    setSelectors(newSelectors);
    // Clear the input field
    setNewSelector({label: '', value: ''});
  }

  const onEditSelectorLabels = (selector: {label: string, value: string}) => {
    const updatedSelectors = selectors.map((s) => {
      if (s.value === selector.value) {
        return selector;
      }
      return s;
    });
    setSelectors(updatedSelectors);
  }

  const onEditSelectorValues = (selector: {label: string, value: string}) => {
    const updatedSelectors = selectors.map((s) => {
      if (s.label === selector.label) {
        return selector;
      }
      return s;
    });
    setSelectors(updatedSelectors);
  }

  const onSaveSelectors = () => {
    setForms([...forms, {name, url, selectors}]);

    // reset fields
    setName('');
    setUrl('');
    setSelectors([]);
    setSelectorLabels([]);
    setSelectorValues([]);
    setIsDataFetched(false);
    setNewSelector({label: '', value: ''});
    setSnackbarMessage('Form saved successfully');
  }

  return (
    <>
    <Box
      component="form"
      noValidate
      autoComplete="off"
      style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}
    >
      <Typography variant="h5"><strong>Add Form</strong></Typography>
      <Box style={{display: 'flex', flexDirection: 'column', flexWrap: 'wrap', gap: '2rem'}}>
        <Box sx={{ '& > :not(style)': { m: 1, width: '30em' } }} style={{display: 'flex', alignItems: 'center', justifyContent: 'space-around'}}>
          <TextField 
            id="name" 
            label="Name" 
            variant="outlined" 
            slotProps={{
              inputLabel: {
                shrink: true,
              }
            }}
            value={name}
            onChange={(e) => setName(e.target.value)} 
          />
          <TextField 
            id="url" 
            label="URL" 
            variant="outlined"
            slotProps={{
              inputLabel: {
                shrink: true,
              }
            }}
            value={url}
            onChange={(e) => setUrl(e.target.value)} 
          />
        </Box>
        
        <LoadingButton 
          style={{marginLeft: 'auto'}} 
          variant="contained"
          loading={loading}
          startIcon={<PsychologyIcon />}
          loadingPosition='start'
          onClick={onGenerateClick}
        >
          Generate
        </LoadingButton>
      </Box>
      {loading && <Box style={{height: '20rem', display: 'flex', justifyContent: 'center', alignItems: 'center'}} ><LoadingSpinner /></Box>}
      <Box sx={{ '& > :not(style)': { m: 1, width: '30em' } }} style={{display: 'grid', gridTemplateColumns: '1fr 1fr 40px', alignItems: 'center', gap: '0.5rem'}}>
        {selectors.map((selector, i) => {
          return (
            <Fragment key={i}>
              <Box style={{display: 'flex', flexDirection: 'column', gap: '0.75rem'}}>
                <Autocomplete
                  freeSolo
                  value={selector.label}
                  onInputChange={(event, newInputValue) => {
                    onEditSelectorLabels({label: newInputValue, value: selector.value});
                  }}
                  options={selectorLabels.map((option) => option)}
                  renderInput={(params) => <TextField {...params} slotProps={{
                    inputLabel: {
                      shrink: true,
                    }
                  }} label={"Label"} />}
                />
              </Box>
              <Box style={{display: 'flex', flexDirection: 'column', gap: '0.75rem'}}>
                <Autocomplete
                  freeSolo
                  value={selector.value}
                  onInputChange={(event, newInputValue) => {
                    onEditSelectorValues({label: selector.label, value: newInputValue});
                  }}
                  options={selectorValues.map((option) => option)}
                  renderInput={(params) => <TextField {...params} slotProps={{
                    inputLabel: {
                      shrink: true,
                    }
                  }} label={"Value"} />}
                />
              </Box>
              <IconButton aria-label="delete" onClick={() => onDeleteSelector(selector)} style={{width: 40, height: 40}}>
                <DeleteForeverIcon />
              </IconButton>
          </Fragment>
          )
        })}
      </Box>
      {isDataFetched && 
        <Box style={{marginTop: '5rem', display: 'flex', flexDirection: 'column', gap: '1rem', border: '1px dashed gray', padding: '3rem', paddingBottom: '1rem'}}>
          <Typography style={{alignSelf: 'start'}} variant="h6">Add new selector</Typography>
          <Box style={{display: 'grid', gridTemplateColumns: '1fr 1fr', alignItems: 'center', gap: '1.5rem'}}>
            <Autocomplete
              freeSolo
              inputValue={newSelector.label}
              options={selectorValues.map((option) => option)}
              onInputChange={(event, newInputValue) => {
                setNewSelector({...newSelector, label: newInputValue});
              }}
              renderInput={(params) => <TextField {...params} slotProps={{
                inputLabel: {
                  shrink: true,
                }
              }} label={"Label"} />}
            />
            <Autocomplete
              freeSolo
              value={newSelector.value}
              options={selectorValues.map((option) => option)}
              onInputChange={(event, newInputValue) => {
                setNewSelector({...newSelector, value: newInputValue});
              }}
              renderInput={(params) => <TextField {...params} slotProps={{
                inputLabel: {
                  shrink: true,
                }
              }} label={"Value"} />}
            />
          </Box>
          <Button style={{marginLeft: 'auto'}} variant="contained" onClick={() => onAddSelector(newSelector)}>Add new</Button>
        </Box>
      }
      {isDataFetched && 
        <Button color='success' style={{marginLeft: 'auto'}} variant="contained" onClick={() => onSaveSelectors()}>Save form</Button>

      }
    </Box>
    <Snackbar
      open={snackbarOpen}
      autoHideDuration={6000}
      onClose={handleCloseSnackbar}
      message={snackbarMessage}
    />
    </>
  )
}

export default GeneratedSelectors;