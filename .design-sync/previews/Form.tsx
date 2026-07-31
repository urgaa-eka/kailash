import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  Input,
  Textarea,
  Switch,
  Button,
} from 'frontend';
import { useForm } from 'react-hook-form';

// `Form` is react-hook-form's FormProvider; FormField/FormItem read that
// context, so every cell drives a real useForm() instance. Outside it the parts
// throw "Cannot destructure property 'getFieldState' of useFormContext()".
export const StationDetails = () => {
  const form = useForm({
    defaultValues: { name: 'Urjaa North Hub', capacity: '60' },
  });
  return (
    <Form {...form}>
      <form className="w-[420px] space-y-5">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Station name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormDescription>Shown to drivers in the mobile app.</FormDescription>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="capacity"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Rated capacity (kW)</FormLabel>
              <FormControl>
                <Input type="number" {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        <Button type="submit">Save station</Button>
      </form>
    </Form>
  );
};

export const WithValidationMessage = () => {
  const form = useForm({
    defaultValues: { email: '' },
    errors: { email: { type: 'required', message: 'An operator email is required.' } },
  });
  return (
    <Form {...form}>
      <form className="w-[420px] space-y-5">
        <FormField
          control={form.control}
          name="email"
          rules={{ required: 'An operator email is required.' }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Operator email</FormLabel>
              <FormControl>
                <Input placeholder="ops@go4garage.in" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Invite</Button>
      </form>
    </Form>
  );
};

export const MixedControls = () => {
  const form = useForm({
    defaultValues: { note: 'Connector 3 locked out.', roaming: true },
  });
  return (
    <Form {...form}>
      <form className="w-[420px] space-y-5">
        <FormField
          control={form.control}
          name="note"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Dispatch note</FormLabel>
              <FormControl>
                <Textarea {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="roaming"
          render={({ field }) => (
            <FormItem className="flex items-center justify-between rounded-md border p-4">
              <div className="space-y-0.5">
                <FormLabel>Accept roaming sessions</FormLabel>
                <FormDescription>OCPI partners may start sessions here.</FormDescription>
              </div>
              <FormControl>
                <Switch checked={field.value} onCheckedChange={field.onChange} />
              </FormControl>
            </FormItem>
          )}
        />
      </form>
    </Form>
  );
};
