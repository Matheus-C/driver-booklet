create or replace function sec_to_time(seconds numeric)
returns text
language plpgsql
as $$
begin
  return to_char((seconds || ' seconds')::interval, 'HH24:MI:SS');
end;
$$; 